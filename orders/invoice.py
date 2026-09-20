from decimal import Decimal
from io import BytesIO

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER

# Standard HSN code for gold jewellery (articles of jewellery of precious metal).
# Adjust per your client's actual product mix if they also sell silver/imitation.
HSN_CODE_GOLD_JEWELLERY = '7113'


def generate_invoice_pdf(order):
    """Returns a BytesIO containing a rendered PDF invoice for the given Order."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=20 * mm, bottomMargin=20 * mm,
        leftMargin=18 * mm, rightMargin=18 * mm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title2', parent=styles['Title'], fontSize=16, spaceAfter=2)
    small = ParagraphStyle('Small', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
    right = ParagraphStyle('Right', parent=styles['Normal'], alignment=TA_RIGHT)
    center = ParagraphStyle('Center', parent=styles['Normal'], alignment=TA_CENTER)

    elements = []

    elements.append(Paragraph(settings.BUSINESS_NAME or 'Jewellery Store', title_style))
    if settings.BUSINESS_ADDRESS:
        elements.append(Paragraph(settings.BUSINESS_ADDRESS, small))
    contact_line = []
    if settings.BUSINESS_PHONE:
        contact_line.append(f"Phone: {settings.BUSINESS_PHONE}")
    if settings.BUSINESS_GSTIN:
        contact_line.append(f"GSTIN: {settings.BUSINESS_GSTIN}")
    if contact_line:
        elements.append(Paragraph(' | '.join(contact_line), small))
    elements.append(Spacer(1, 10 * mm))

    invoice_no = f"INV-{order.pk:05d}"
    meta_table = Table([
        [
            Paragraph(f"<b>Invoice No:</b> {invoice_no}<br/><b>Date:</b> {order.order_date.strftime('%d %b %Y')}", styles['Normal']),
            Paragraph(
                f"<b>Billed To:</b><br/>{order.user.get_full_name() or order.user.username}"
                f"<br/>{order.user.email}" + (f"<br/>{order.user.phone}" if order.user.phone else ''),
                styles['Normal'],
            ),
        ]
    ], colWidths=[90 * mm, 80 * mm])
    meta_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(meta_table)
    elements.append(Spacer(1, 8 * mm))

    from catalogue.models import calculate_price

    metal_type = order.jewellery.metal_type if order.jewellery else (
        order.custom_request.metal_type if order.custom_request else 'gold'
    )
    weight = order.jewellery.weight if order.jewellery else (
        order.custom_request.weight if order.custom_request else Decimal('0')
    )
    making_charge = order.jewellery.making_charge if order.jewellery else (
        order.custom_request.goldsmith_making_charge or Decimal('0') if order.custom_request else Decimal('0')
    )

    try:
        breakdown = calculate_price(weight, metal_type, making_charge)
    except ValueError:
        breakdown = None

    data = [['Description', 'HSN', 'Weight (g)', 'Rate/g (Rs.)', 'Making Charge (Rs.)', 'Taxable Value (Rs.)']]
    if breakdown:
        data.append([
            order.item_name, HSN_CODE_GOLD_JEWELLERY, f"{weight}",
            f"{breakdown['rate_per_gram']}", f"{breakdown['making_charge']}",
            f"{breakdown['metal_cost'] + float(breakdown['making_charge']):.2f}",
        ])
    else:
        data.append([order.item_name, HSN_CODE_GOLD_JEWELLERY, f"{weight}", '-', '-', f"{order.total_amount}"])

    item_table = Table(data, colWidths=[45 * mm, 18 * mm, 22 * mm, 25 * mm, 32 * mm, 28 * mm])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b6b1f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(item_table)
    elements.append(Spacer(1, 6 * mm))

    if breakdown:
        taxable_value = breakdown['metal_cost'] + float(breakdown['making_charge'])
        gst_total = float(breakdown['gst_amount'])
        cgst = round(gst_total / 2, 2)
        sgst = round(gst_total / 2, 2)
        totals_data = [
            ['Taxable Value', f"Rs. {taxable_value:.2f}"],
            [f"CGST ({breakdown['gst_percent'] / 2}%)", f"Rs. {cgst}"],
            [f"SGST ({breakdown['gst_percent'] / 2}%)", f"Rs. {sgst}"],
            ['Total Amount', f"Rs. {breakdown['total']}"],
        ]
    else:
        totals_data = [['Total Amount', f"Rs. {order.total_amount}"]]

    totals_table = Table(totals_data, colWidths=[130 * mm, 40 * mm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 0.75, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 6 * mm))

    elements.append(Paragraph(
        f"<b>Paid:</b> Rs. {order.advance_payment} &nbsp;&nbsp; "
        f"<b>Balance Due:</b> Rs. {order.remaining_amount} &nbsp;&nbsp; "
        f"<b>Order Status:</b> {order.get_status_display()}",
        styles['Normal'],
    ))
    elements.append(Spacer(1, 10 * mm))
    elements.append(Paragraph(
        "This is a computer-generated invoice. Please verify hallmarking/purity "
        "certificate details separately with the seller.",
        small,
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
