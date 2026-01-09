"""
Recipe PDF generation.
Creates professional, printable PDF recipes with images.
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path
from io import BytesIO

import httpx
from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors


async def create_recipe_pdf(meal: dict, filepath: Path) -> None:
    """
    Create a professional, printable PDF recipe with image.
    
    Args:
        meal: Dictionary containing meal data from TheMealDB API
        filepath: Path where the PDF should be saved
    """
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=12,
        alignment=1,  # Center
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495E'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#2C3E50')
    )
    
    # Recipe title
    title = Paragraph(meal.get('strMeal', 'Unknown Recipe'), title_style)
    story.append(title)
    
    # Recipe info
    info_data = [
        ['Category:', meal.get('strCategory', 'N/A')],
        ['Cuisine:', meal.get('strArea', 'N/A')],
        ['Tags:', meal.get('strTags', 'N/A')],
    ]
    
    info_table = Table(info_data, colWidths=[1.2*inch, 4.3*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ECF0F1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2C3E50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Try to add recipe image using async httpx
    image_url = meal.get('strMealThumb')
    temp_img_path = None
    if image_url:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                
                img_data = BytesIO(response.content)
                img = PILImage.open(img_data)
                
                # Resize image for PDF (max 4 inches wide)
                max_width = 4 * inch
                width_ratio = max_width / img.width
                new_height = img.height * width_ratio
                
                # Save resized image to temporary file
                resized_img = img.resize((int(max_width), int(new_height)), PILImage.Resampling.LANCZOS)
                
                # Create temporary file for the image
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    temp_img_path = tmp_file.name
                    resized_img.save(temp_img_path, format='JPEG', quality=95)
                
                # Add image to PDF
                pdf_img = Image(temp_img_path, width=max_width, height=new_height)
                story.append(pdf_img)
                story.append(Spacer(1, 0.2*inch))
                
        except httpx.TimeoutException:
            # Image download timed out, continue without image
            pass
        except httpx.HTTPStatusError as e:
            # HTTP error (404, 500, etc.), continue without image
            pass
        except httpx.RequestError as e:
            # Network error, continue without image
            pass
        except (IOError, OSError) as e:
            # Image processing or file system error
            pass
        except Exception as e:
            # Any other unexpected error, continue without image
            pass
    
    # Ingredients section
    story.append(Paragraph("INGREDIENTS", heading_style))
    
    ingredients = []
    for i in range(1, 21):
        ingredient = meal.get(f"strIngredient{i}", "")
        measure = meal.get(f"strMeasure{i}", "")
        if ingredient and ingredient.strip():
            ingredients.append([
                f"{measure.strip()}",
                ingredient.strip()
            ])
    
    if ingredients:
        ing_table = Table(ingredients, colWidths=[1.5*inch, 4*inch])
        ing_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2C3E50')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ECF0F1')),
        ]))
        story.append(ing_table)
    else:
        story.append(Paragraph("No ingredients listed", normal_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Instructions section
    story.append(Paragraph("INSTRUCTIONS", heading_style))
    instructions = meal.get('strInstructions', 'No instructions available')
    story.append(Paragraph(instructions, normal_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}"
    story.append(Paragraph(footer_text, ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#95A5A6'),
        alignment=1
    )))
    
    # Build PDF
    doc.build(story)
    
    # Clean up temporary image file if it was created
    if temp_img_path and os.path.exists(temp_img_path):
        try:
            os.unlink(temp_img_path)
        except Exception:
            pass
