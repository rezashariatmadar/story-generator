import io
import logging
from datetime import datetime
from typing import List, Dict, Any, Union, Optional
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.text import slugify
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.colors import black, blue, gray
import zipfile
import json

logger = logging.getLogger(__name__)

class StoryExportService:
    """
    Service for exporting stories in various formats
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for PDF generation"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=blue,
            alignment=1  # Center alignment
        )
        
        # Metadata style
        self.meta_style = ParagraphStyle(
            'CustomMeta',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=gray,
            spaceAfter=20
        )
        
        # Content style
        self.content_style = ParagraphStyle(
            'CustomContent',
            parent=self.styles['Normal'],
            fontSize=12,
            leading=18,
            spaceAfter=12,
            alignment=4  # Justify
        )
        
        # Keywords style
        self.keywords_style = ParagraphStyle(
            'CustomKeywords',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=blue,
            spaceAfter=15,
            leftIndent=20
        )
    
    def export_story_txt(self, story) -> HttpResponse:
        """Export single story as TXT file"""
        try:
            content = self._generate_txt_content(story)
            
            response = HttpResponse(content, content_type='text/plain')
            filename = f"{slugify(story.title or 'story')}_{story.id}.txt"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            logger.error(f"Error exporting story {story.id} as TXT: {e}")
            raise
    
    def export_story_pdf(self, story) -> HttpResponse:
        """Export single story as PDF file"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=inch, bottomMargin=inch)
            
            story_elements = self._build_pdf_elements(story)
            doc.build(story_elements)
            
            buffer.seek(0)
            
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            filename = f"{slugify(story.title or 'story')}_{story.id}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            logger.error(f"Error exporting story {story.id} as PDF: {e}")
            raise
    
    def export_story_html(self, story) -> HttpResponse:
        """Export single story as HTML file"""
        try:
            context = {
                'story': story,
                'export_date': datetime.now(),
                'word_count': story.word_count
            }
            
            html_content = render_to_string('exports/story_export.html', context)
            
            response = HttpResponse(html_content, content_type='text/html')
            filename = f"{slugify(story.title or 'story')}_{story.id}.html"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            logger.error(f"Error exporting story {story.id} as HTML: {e}")
            raise
    
    def export_multiple_stories_zip(self, stories: List, format_type: str = 'txt') -> HttpResponse:
        """Export multiple stories as a ZIP archive"""
        try:
            buffer = io.BytesIO()
            
            with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for story in stories:
                    if format_type == 'txt':
                        content = self._generate_txt_content(story)
                        filename = f"{slugify(story.title or 'story')}_{story.id}.txt"
                    elif format_type == 'pdf':
                        content = self._generate_pdf_content(story)
                        filename = f"{slugify(story.title or 'story')}_{story.id}.pdf"
                    elif format_type == 'html':
                        content = self._generate_html_content(story)
                        filename = f"{slugify(story.title or 'story')}_{story.id}.html"
                    else:
                        continue
                    
                    zip_file.writestr(filename, content)
                
                # Add a metadata file
                metadata = self._generate_collection_metadata(stories)
                zip_file.writestr('collection_info.json', json.dumps(metadata, indent=2))
            
            buffer.seek(0)
            
            response = HttpResponse(buffer.getvalue(), content_type='application/zip')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"stories_collection_{timestamp}.zip"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            logger.error(f"Error exporting multiple stories as ZIP: {e}")
            raise
    
    def export_user_collection(self, user, format_type: str = 'txt', include_metadata: bool = True) -> HttpResponse:
        """Export all user stories as a collection"""
        from .models import Story
        
        try:
            stories = Story.objects.filter(user=user).order_by('-created_at')
            
            if not stories.exists():
                raise ValueError("No stories found for export")
            
            return self.export_multiple_stories_zip(stories, format_type)
            
        except Exception as e:
            logger.error(f"Error exporting user collection for {user.username}: {e}")
            raise
    
    def _generate_txt_content(self, story) -> str:
        """Generate TXT content for a story"""
        lines = [
            f"Title: {story.title or 'Untitled Story'}",
            f"Author: {story.user.username}",
            f"Created: {story.created_at.strftime('%B %d, %Y at %I:%M %p')}",
            f"Genre: {story.get_genre_display()}",
            f"Length: {story.get_length_display()}",
            f"Tone: {story.get_tone_display()}",
            f"Keywords: {story.keywords}",
            f"Word Count: {story.word_count} words",
            ""
        ]
        
        if story.rating:
            lines.append(f"Rating: {story.rating}/5 stars")
            lines.append("")
        
        if story.ai_model_used != 'simple_algorithm':
            lines.append(f"Generated with: {story.ai_model_used}")
            lines.append("")
        
        lines.extend([
            "=" * 60,
            "STORY CONTENT",
            "=" * 60,
            "",
            story.content,
            "",
            "=" * 60,
            f"Exported from AI Story Generator on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            "https://github.com/your-username/ai-story-generator"
        ])
        
        return "\n".join(lines)
    
    def _generate_pdf_content(self, story) -> bytes:
        """Generate PDF content for a story"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=inch, bottomMargin=inch)
        
        story_elements = self._build_pdf_elements(story)
        doc.build(story_elements)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def _generate_html_content(self, story) -> str:
        """Generate HTML content for a story"""
        context = {
            'story': story,
            'export_date': datetime.now(),
            'word_count': story.word_count
        }
        
        return render_to_string('exports/story_export.html', context)
    
    def _build_pdf_elements(self, story):
        """Build PDF elements for ReportLab"""
        elements = []
        
        # Title
        title = story.title or "Untitled Story"
        elements.append(Paragraph(title, self.title_style))
        elements.append(Spacer(1, 20))
        
        # Metadata
        metadata_lines = [
            f"<b>Author:</b> {story.user.username}",
            f"<b>Created:</b> {story.created_at.strftime('%B %d, %Y at %I:%M %p')}",
            f"<b>Genre:</b> {story.get_genre_display()}",
            f"<b>Length:</b> {story.get_length_display()}",
            f"<b>Tone:</b> {story.get_tone_display()}",
            f"<b>Word Count:</b> {story.word_count} words"
        ]
        
        if story.rating:
            metadata_lines.append(f"<b>Rating:</b> {story.rating}/5 stars")
        
        if story.ai_model_used != 'simple_algorithm':
            metadata_lines.append(f"<b>Generated with:</b> {story.ai_model_used}")
        
        for line in metadata_lines:
            elements.append(Paragraph(line, self.meta_style))
        
        elements.append(Spacer(1, 10))
        
        # Keywords
        keywords_text = f"<b>Keywords:</b> {story.keywords}"
        elements.append(Paragraph(keywords_text, self.keywords_style))
        elements.append(Spacer(1, 20))
        
        # Story content
        # Split content into paragraphs for better formatting
        paragraphs = story.content.split('\n\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                elements.append(Paragraph(paragraph.strip(), self.content_style))
                elements.append(Spacer(1, 6))
        
        # Footer
        elements.append(Spacer(1, 30))
        footer_text = f"Exported from AI Story Generator on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        elements.append(Paragraph(footer_text, self.meta_style))
        
        return elements
    
    def _generate_collection_metadata(self, stories) -> Dict[str, Any]:
        """Generate metadata for a collection of stories"""
        if not stories:
            return {}
        
        # Get statistics
        total_stories = len(stories)
        total_words = sum(story.word_count for story in stories)
        avg_words = total_words / total_stories if total_stories > 0 else 0
        
        # Genre distribution
        genres = {}
        for story in stories:
            genre = story.get_genre_display()
            genres[genre] = genres.get(genre, 0) + 1
        
        # Rating statistics
        rated_stories = [s for s in stories if s.rating]
        avg_rating = sum(s.rating for s in rated_stories) / len(rated_stories) if rated_stories else None
        
        # AI vs Template stories
        ai_stories = sum(1 for s in stories if s.ai_model_used != 'simple_algorithm')
        template_stories = total_stories - ai_stories
        
        return {
            'collection_info': {
                'title': f'Story Collection - {stories[0].user.username}',
                'author': stories[0].user.username,
                'export_date': datetime.now().isoformat(),
                'total_stories': total_stories,
                'date_range': {
                    'oldest': min(s.created_at for s in stories).isoformat(),
                    'newest': max(s.created_at for s in stories).isoformat()
                }
            },
            'statistics': {
                'total_words': total_words,
                'average_words_per_story': round(avg_words, 1),
                'average_rating': round(avg_rating, 1) if avg_rating else None,
                'genre_distribution': genres,
                'generation_methods': {
                    'ai_generated': ai_stories,
                    'template_based': template_stories
                }
            },
            'stories': [
                {
                    'id': story.id,
                    'title': story.title or 'Untitled',
                    'created_at': story.created_at.isoformat(),
                    'genre': story.get_genre_display(),
                    'word_count': story.word_count,
                    'rating': story.rating,
                    'is_favorite': story.is_favorite,
                    'ai_model': story.ai_model_used
                }
                for story in stories
            ]
        }

# Global instance for easy importing
export_service = StoryExportService()

# Standalone functions for compatibility
def export_story_txt(story):
    """Export story as TXT - standalone function"""
    return export_service.export_story_txt(story)

def export_story_html(story):
    """Export story as HTML - standalone function"""
    return export_service.export_story_html(story)

def export_story_pdf(story):
    """Export story as PDF - standalone function"""
    return export_service.export_story_pdf(story) 