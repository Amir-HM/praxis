"""
Rättskoll OCR Test - Sample Document Generator
===============================================
Creates a sample PDF for testing OCR pipeline.
Run this if you don't have a real FUP to test with.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path


def create_sample_fup(output_path: str = "test_docs/sample_fup.pdf"):
    """Create a sample Swedish FUP-style PDF for testing."""
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        name='SwedishTitle',
        parent=styles['Title'],
        fontSize=16,
        spaceAfter=20
    ))
    
    styles.add(ParagraphStyle(
        name='SwedishHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=10,
        spaceBefore=15
    ))
    
    story = []
    
    # Page 1: Title and case info
    story.append(Paragraph("FÖRUNDERSÖKNINGSPROTOKOLL", styles['SwedishTitle']))
    story.append(Paragraph("(TESTDOKUMENT FÖR OCR-VALIDERING)", styles['Normal']))
    story.append(Spacer(1, 20))
    
    case_data = [
        ["Målnummer:", "B 1234-25"],
        ["Datum:", "2025-01-15"],
        ["Åklagarmyndighet:", "Stockholm"],
        ["Handläggare:", "Kriminalinspektör Erik Johansson"],
    ]
    
    case_table = Table(case_data, colWidths=[4*cm, 8*cm])
    case_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(case_table)
    story.append(Spacer(1, 30))
    
    # Case summary
    story.append(Paragraph("SAMMANFATTNING AV ÄRENDET", styles['SwedishHeading']))
    story.append(Paragraph(
        "Detta ärende rör misstänkt stöld som ska ha ägt rum den 15 januari 2025 "
        "vid Stortorget i Stockholm. Den misstänkte, Erik Lindberg, förnekar brott. "
        "Utredningen omfattar vittnesförhör, telefonloggar och teknisk bevisning.",
        styles['Normal']
    ))
    story.append(Spacer(1, 20))
    
    # Page 2: Witness statement 1
    story.append(Paragraph("VITTNESFÖRHÖR - Anna Svensson", styles['SwedishHeading']))
    story.append(Paragraph("Förhöret hållet: 2025-01-16 kl 14:00", styles['Normal']))
    story.append(Paragraph("Förhörsledare: Polisassistent Maria Berg", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        '"Jag befann mig vid Stortorget den 15 januari ungefär klockan 14:30. '
        'Jag såg en man som jag tror var den misstänkte. Han hade en blå jacka '
        'och verkade nervös. Han sprang iväg mot tunnelbanan efter att ha tagit '
        'något från en av butikerna."',
        styles['Normal']
    ))
    story.append(Spacer(1, 20))
    
    # Witness statement 2
    story.append(Paragraph("VITTNESFÖRHÖR - Lars Pettersson", styles['SwedishHeading']))
    story.append(Paragraph("Förhöret hållet: 2025-01-16 kl 16:30", styles['Normal']))
    story.append(Paragraph("Förhörsledare: Polisassistent Johan Eriksson", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        '"Jag var på Stortorget vid lunchtid, runt klockan 12:00-12:30. '
        'Jag såg en man med svart jacka som betedde sig konstigt. '
        'Han stod och tittade in i butiken länge innan han gick in."',
        styles['Normal']
    ))
    story.append(Spacer(1, 30))
    
    # Page 3: Phone records
    story.append(Paragraph("TELEFONLOGGAR", styles['SwedishHeading']))
    story.append(Paragraph("Abonnent: Erik Lindberg (misstänkt)", styles['Normal']))
    story.append(Spacer(1, 10))
    
    phone_data = [
        ["Datum", "Tid", "Typ", "Mast/Plats", "Motpart"],
        ["2025-01-15", "12:05", "Samtal ut", "Södermalm", "+46701234567"],
        ["2025-01-15", "14:15", "Samtal in", "Södermalm", "+46709876543"],
        ["2025-01-15", "14:45", "SMS", "Södermalm", "+46701234567"],
        ["2025-01-15", "16:30", "Samtal ut", "Gamla Stan", "+46705555555"],
    ]
    
    phone_table = Table(phone_data, colWidths=[2.5*cm, 2*cm, 2.5*cm, 3*cm, 3*cm])
    phone_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(phone_table)
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Anmärkning: Mastpositioner visar att den misstänktes telefon befann sig "
        "i Södermalm mellan kl 12:00 och 15:00. Stortorget ligger cirka 5 km från Södermalm.",
        styles['Normal']
    ))
    story.append(Spacer(1, 30))
    
    # Page 4: Suspect interrogation
    story.append(Paragraph("FÖRHÖR MED MISSTÄNKT - Erik Lindberg", styles['SwedishHeading']))
    story.append(Paragraph("Förhöret hållet: 2025-01-17 kl 10:00", styles['Normal']))
    story.append(Paragraph("Förhörsledare: Kriminalinspektör Erik Johansson", styles['Normal']))
    story.append(Paragraph("Försvarare: Advokat Karin Holm närvarande", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        '"Jag var hemma hela dagen den 15 januari. Jag gick aldrig till Stortorget. '
        'Jag minns att jag pratade i telefon med min kompis på förmiddagen och sen '
        'tittade jag på TV resten av dagen. Jag förstår inte varför jag är misstänkt."',
        styles['Normal']
    ))
    story.append(Spacer(1, 30))
    
    # Note about inconsistencies (for testing)
    story.append(Paragraph("POTENTIELLA INKONSISTENSER (TESTDATA)", styles['SwedishHeading']))
    story.append(Paragraph(
        "Detta testdokument innehåller avsiktliga inkonsistenser för att testa "
        "Rättskoll-systemet:",
        styles['Normal']
    ))
    story.append(Spacer(1, 5))
    
    issues = [
        "1. Vittnenas tidpunkter: Anna säger 14:30, Lars säger 12:00-12:30",
        "2. Jackans färg: Anna säger blå, Lars säger svart",
        "3. Telefonlogg vs vittne: Anna såg misstänkt på Stortorget 14:30, men telefonen var i Södermalm 14:15 (5 km bort, 15 min mellanrum)",
        "4. Misstänktes alibi: Säger sig ha varit hemma hela dagen, men telefonloggar visar rörelse mellan områden",
    ]
    
    for issue in issues:
        story.append(Paragraph(issue, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    print(f"✅ Created sample FUP: {output_path}")
    return output_path


if __name__ == "__main__":
    create_sample_fup()
