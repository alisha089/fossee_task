from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from django.http import HttpResponse
from .models import FileUpload, Equipment
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny] # Allow anyone to sign up

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=201)
        return Response(serializer.errors, status=400)

class UploadCSVView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        file_obj = request.FILES['file']
        
        # 1. Read CSV using Pandas
        try:
            df = pd.read_csv(file_obj)
        except Exception as e:
            return Response({"error": "Invalid CSV file"}, status=400)

        # 2. Calculate Stats
        stats = {
            "total_count": len(df),
            "avg_flowrate": float(df['Flowrate'].mean()),
            "avg_pressure": float(df['Pressure'].mean()),
            "avg_temperature": float(df['Temperature'].mean())
        }

        # 3. Save FileUpload Record LINKED TO USER
        upload_instance = FileUpload.objects.create(
            user=request.user,  # <--- CHANGED: Link to current user
            file=file_obj,
            **stats
        )

        # 4. Save Equipment Data (Bulk Create)
        equipment_list = [
            Equipment(
                upload=upload_instance,
                name=row['Equipment Name'],
                eq_type=row['Type'],
                flowrate=row['Flowrate'],
                pressure=row['Pressure'],
                temperature=row['Temperature']
            ) for _, row in df.iterrows()
        ]
        Equipment.objects.bulk_create(equipment_list)

        # 5. Maintain History (Keep only last 5 FOR THIS USER)
        # <--- CHANGED: Filter by user=request.user
        user_uploads = FileUpload.objects.filter(user=request.user).order_by('-uploaded_at')
        if user_uploads.count() > 5:
            old_uploads = user_uploads[5:]
            for old in old_uploads:
                old.delete()

        # 6. Prepare Response Data
        type_distribution = df['Type'].value_counts().to_dict()
        
        return Response({
            "id": upload_instance.id,
            "stats": stats,
            "distribution": type_distribution,
            "data": df.to_dict(orient='records')
        })

class HistoryView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        uploads = FileUpload.objects.filter(user=request.user).order_by('-uploaded_at')[:5]
        data = []
        for u in uploads:
            # Extract just the filename from the full path
            filename = u.file.name.split('/')[-1] 
            
            data.append({
                "id": u.id,
                "filename": filename,  # <--- NEW FIELD
                "date": u.uploaded_at.strftime("%Y-%m-%d %I:%M %p"),
                "count": u.total_count,
                "avg_flowrate": u.avg_flowrate,
                "avg_pressure": u.avg_pressure,
                "avg_temperature": u.avg_temperature
            })
        return Response(data)


class GeneratePDFView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, upload_id):
        try:
            # <--- CHANGED: Ensure user owns the file
            upload = FileUpload.objects.get(id=upload_id, user=request.user)
        except FileUpload.DoesNotExist:
            return Response({"error": "Not Found"}, status=404)

        # Get all equipment for this upload
        equipment = Equipment.objects.filter(upload=upload)

        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        title = Paragraph(f"<b>Chemical Equipment Report - Upload #{upload.id}</b>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.3 * 72))

        # Summary Stats
        summary = Paragraph(
            f"<b>Summary Statistics:</b><br/>"
            f"Date: {upload.uploaded_at.strftime('%Y-%m-%d %I:%M %p')}<br/>"
            f"Total Equipment: {upload.total_count}<br/>"
            f"Average Flowrate: {upload.avg_flowrate:.2f}<br/>"
            f"Average Pressure: {upload.avg_pressure:.2f}<br/>"
            f"Average Temperature: {upload.avg_temperature:.2f}",
            styles['Normal']
        )
        elements.append(summary)
        elements.append(Spacer(1, 0.3 * 72))

        # Data Table
        table_data = [['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']]
        for eq in equipment[:10]:  # Show first 10 rows
            table_data.append([
                eq.name,
                eq.eq_type,
                f"{eq.flowrate:.2f}",
                f"{eq.pressure:.2f}",
                f"{eq.temperature:.2f}"
            ])

        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)

        # Build PDF
        doc.build(elements)
        buffer.seek(0)

        # Return as download
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="report_{upload_id}.pdf"'
        return response
