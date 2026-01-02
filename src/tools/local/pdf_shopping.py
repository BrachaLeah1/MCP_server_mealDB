"""
Shopping list PDF generation.
Creates professional, printable shopping list PDFs organized by category.
"""

from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

from .categories import get_ingredient_category


def create_shopping_list_pdf(meal_names: list, all_ingredients: dict, filepath: Path) -> None:
    """
    Create a professional, printable shopping list PDF.
    
    Args:
        meal_names: List of recipe names included in the shopping list
        all_ingredients: Dictionary of ingredients with structure:
            {ingredient_key: {'original': str, 'measures': list, 'recipes': list}}
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
        textColor=colors.HexColor('#27AE60'),
        spaceAfter=12,
        alignment=1,  # Center
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#34495E'),
        spaceAfter=8,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    # Title
    title = Paragraph("Shopping List", title_style)
    story.append(title)
    story.append(Spacer(1, 0.2*inch))
    
    # Recipes section
    story.append(Paragraph("Recipes", heading_style))
    
    recipes_data = [[f"{i}.", name] for i, name in enumerate(meal_names, 1)]
    
    if recipes_data:
        recipes_table = Table(recipes_data, colWidths=[0.4*inch, 6.1*inch])
        recipes_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E8F8F5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2C3E50')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
        ]))
        story.append(recipes_table)
    
    story.append(Spacer(1, 0.3*inch))
    
    # Ingredients section
    story.append(Paragraph("Ingredients", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Sort ingredients alphabetically
    sorted_ingredients = sorted(all_ingredients.items(), key=lambda x: x[1]['original'].lower())
    
    # Group by category
    categorized = {}
    for ing_key, ing_data in sorted_ingredients:
        category = get_ingredient_category(ing_data['original'])
        if category not in categorized:
            categorized[category] = []
        categorized[category].append((ing_key, ing_data))
    
    # Display ingredients by category
    for category in sorted(categorized.keys()):
        # Category heading
        story.append(Paragraph(category, subheading_style))
        
        # Build ingredient table for this category
        ing_rows = []
        for ing_key, ing_data in categorized[category]:
            # Checkbox symbol (☐)
            checkbox = "☐"
            
            # Format ingredient name and measure
            if ing_data['measures']:
                measure_str = ', '.join(ing_data['measures'])
                ingredient_text = f"{checkbox}  {ing_data['original'].title()} ({measure_str})"
            else:
                ingredient_text = f"{checkbox}  {ing_data['original'].title()}"
            
            # Recipe reference
            recipe_str = ', '.join(set(ing_data['recipes']))
            
            ing_rows.append([ingredient_text, f"for: {recipe_str}"])
        
        if ing_rows:
            category_table = Table(ing_rows, colWidths=[3*inch, 3.5*inch])
            category_table.setStyle(TableStyle([
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2C3E50')),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (0, -1), 10),
                ('FONTSIZE', (1, 0), (1, -1), 8),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#7F8C8D')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#ECF0F1')),
            ]))
            story.append(category_table)
        
        story.append(Spacer(1, 0.15*inch))
    
    # Summary
    story.append(Spacer(1, 0.2*inch))
    summary_data = [
        ['Total Recipes:', str(len(meal_names))],
        ['Total Ingredients:', str(len(all_ingredients))],
        ['Generated:', datetime.now().strftime('%B %d, %Y at %I:%M %p')],
    ]
    
    summary_table = Table(summary_data, colWidths=[1.5*inch, 5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9F9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2C3E50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
    ]))
    story.append(summary_table)
    
    # Build PDF
    doc.build(story)