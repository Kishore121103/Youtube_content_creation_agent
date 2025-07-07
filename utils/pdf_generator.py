from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Frame
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import HexColor
from reportlab.platypus.flowables import Flowable
import io

# Custom Flowable for drawing a colored box around content
class ApproachContainer(Flowable):
    def __init__(self, content_flowables, background_color=None, border_color=None, padding=10):
        Flowable.__init__(self)
        self.content_flowables = content_flowables
        self.background_color = background_color
        self.border_color = border_color
        self.padding = padding
        self.width = 0
        self.height = 0

    def wrap(self, availWidth, availHeight):
        # Calculate the required width and height for the content
        # This is a simplified wrap, for complex layouts, a Frame might be better
        max_width = 0
        total_height = 0
        for f in self.content_flowables:
            w, h = f.wrapOn(self.canv, availWidth - 2 * self.padding, availHeight - 2 * self.padding)
            max_width = max(max_width, w)
            total_height += h
        self.width = max_width + 2 * self.padding
        self.height = total_height + 2 * self.padding
        return self.width, self.height

    def draw(self):
        canvas = self.canv
        # Draw background rectangle
        if self.background_color:
            canvas.setFillColor(self.background_color)
            canvas.rect(0, 0, self.width, self.height, fill=1)

        # Draw border
        if self.border_color:
            canvas.setStrokeColor(self.border_color)
            canvas.rect(0, 0, self.width, self.height, stroke=1)

        # Draw content
        text_frame = Frame(self.padding, self.padding,
                            self.width - 2 * self.padding, self.height - 2 * self.padding,
                            leftPadding=0, bottomPadding=0,
                            rightPadding=0, topPadding=0,
                            showBoundary=0)
        text_frame.addFromList(self.content_flowables, canvas)


class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._define_custom_styles()

    def _define_custom_styles(self):
        # Base styles, dynamic properties will be applied on top
        self.styles.add(ParagraphStyle(name='DynamicHeading1', parent=self.styles['h1']))
        self.styles.add(ParagraphStyle(name='DynamicParagraph', parent=self.styles['Normal']))
        self.styles.add(ParagraphStyle(name='DynamicSectionHeading', parent=self.styles['h2']))
        self.styles.add(ParagraphStyle(name='DynamicSubHeading', parent=self.styles['h3']))
        self.styles.add(ParagraphStyle(name='DynamicListItem', parent=self.styles['Normal']))
        self.styles.add(ParagraphStyle(name='DynamicCodeBlock', parent=self.styles['Code']))
        self.styles.add(ParagraphStyle(name='DynamicKeyValue', parent=self.styles['Normal']))
        self.styles.add(ParagraphStyle(name='DynamicHeading3', parent=self.styles['h3']))

    def _get_dynamic_style(self, base_style_name, style_dict):
        # Create a new ParagraphStyle based on a base style and a style dictionary
        new_style = ParagraphStyle(name=f"{base_style_name}_dynamic", parent=self.styles[base_style_name])

        if 'font_size' in style_dict:
            new_style.fontSize = style_dict['font_size']
            new_style.leading = style_dict['font_size'] * 1.2 # Default leading

        if 'text_color' in style_dict:
            new_style.textColor = HexColor(style_dict['text_color'])

        if 'alignment' in style_dict:
            if style_dict['alignment'] == 'center':
                new_style.alignment = TA_CENTER
            elif style_dict['alignment'] == 'left':
                new_style.alignment = TA_LEFT

        if 'space_before' in style_dict:
            new_style.spaceBefore = style_dict['space_before']
        if 'space_after' in style_dict:
            new_style.spaceAfter = style_dict['space_after']
        if 'left_indent' in style_dict:
            new_style.leftIndent = style_dict['left_indent']
        if 'bullet_color' in style_dict:
            new_style.bulletColor = HexColor(style_dict['bullet_color'])
        if 'background_color' in style_dict:
            new_style.backColor = HexColor(style_dict['background_color'])
        if 'padding' in style_dict:
            new_style.borderPadding = style_dict['padding']
        if 'border_radius' in style_dict:
            new_style.borderRadius = style_dict['border_radius']

        return new_style

    def generate_pdf(self, structured_content: dict) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []

        for section in structured_content.get("sections", []):
            s_type = section["type"]
            s_text = section.get("text", "")
            s_style = section.get("style", {})

            if s_type == "heading":
                style = self._get_dynamic_style('DynamicHeading1', s_style)
                story.append(Paragraph(s_text, style))
                story.append(Spacer(1, s_style.get('space_after', 20)))
                story.append(PageBreak()) # Start new page after main title
            elif s_type == "paragraph":
                style = self._get_dynamic_style('DynamicParagraph', s_style)
                story.append(Paragraph(s_text, style))
            elif s_type == "section_heading":
                style = self._get_dynamic_style('DynamicSectionHeading', s_style)
                story.append(Paragraph(s_text, style))
                story.append(Spacer(1, s_style.get('space_after', 15)))
            elif s_type == "sub_heading":
                style = self._get_dynamic_style('DynamicSubHeading', s_style)
                story.append(Paragraph(s_text, style))
                story.append(Spacer(1, s_style.get('space_after', 5)))
            elif s_type == "code_block":
                style = self._get_dynamic_style('DynamicCodeBlock', s_style)
                story.append(Paragraph(s_text, style))
            elif s_type == "list_item":
                style = self._get_dynamic_style('DynamicListItem', s_style)
                story.append(Paragraph(f"• {s_text}", style))
            elif s_type == "key_value_list":
                for item in section["data"]:
                    key_style = self._get_dynamic_style('DynamicKeyValue', item.get('style', {}))
                    # Apply key_color if present
                    if 'key_color' in item.get('style', {}):
                        key_style.textColor = HexColor(item['style']['key_color'])
                    story.append(Paragraph(f"<b>{item['key']}:</b> {item['value']}", key_style))
                    story.append(Spacer(1, item.get('style', {}).get('space_after', 5)))
            elif s_type == "list": # For suggested titles
                heading_style = self._get_dynamic_style('DynamicSubHeading', s_style)
                story.append(Paragraph(f"<b>{section.get('heading', '')}:</b>", heading_style))
                for item in section["items"]:
                    item_style = self._get_dynamic_style('DynamicListItem', s_style)
                    story.append(Paragraph(f"• {item}", item_style))
                story.append(Spacer(1, s_style.get('space_after', 10)))
            elif s_type == "approach":
                approach_flowables = []
                # Approach Title
                title_style = self._get_dynamic_style('DynamicHeading3', section['style'])
                if 'title_font_size' in section['style']:
                    title_style.fontSize = section['style']['title_font_size']
                if 'title_text_color' in section['style']:
                    title_style.textColor = HexColor(section['style']['title_text_color'])
                approach_flowables.append(Paragraph(section["title"], title_style))
                approach_flowables.append(Spacer(1, 5))

                for item in section["content"]:
                    item_type = item["type"]
                    item_text = item.get("text", "")
                    item_style = item.get("style", {})

                    if item_type == "paragraph":
                        style = self._get_dynamic_style('DynamicParagraph', item_style)
                        approach_flowables.append(Paragraph(item_text, style))
                    elif item_type == "sub_heading":
                        style = self._get_dynamic_style('DynamicSubHeading', item_style)
                        approach_flowables.append(Paragraph(item_text, style))
                    elif item_type == "code_block":
                        style = self._get_dynamic_style('DynamicCodeBlock', item_style)
                        approach_flowables.append(Paragraph(item_text, style))
                    elif item_type == "list_item":
                        style = self._get_dynamic_style('DynamicListItem', item_style)
                        approach_flowables.append(Paragraph(f"• {item_text}", style))
                    
                    # Add space after each item within the approach
                    if 'space_after' in item_style:
                        approach_flowables.append(Spacer(1, item_style['space_after']))

                # Add the approach container to the main story
                story.append(ApproachContainer(
                    approach_flowables,
                    background_color=HexColor(section['style'].get('box_background_color', '#FFFFFF')),
                    border_color=HexColor(section['style'].get('box_border_color', '#CCCCCC')),
                    padding=section['style'].get('padding', 10)
                ))
                story.append(Spacer(1, section['style'].get('space_after', 15))) # Space after the entire approach box

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()