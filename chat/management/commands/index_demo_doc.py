from django.core.management.base import BaseCommand
from django.conf import settings
import os
from chat.rag_service import index_document

class Command(BaseCommand):
    help = 'Index a demo document for RAG testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            help='Path to the document file'
        )
        parser.add_argument(
            '--title',
            type=str,
            default='Demo Document',
            help='Title for the document'
        )

    def handle(self, *args, **options):
        file_path = options['path']
        title = options['title']
        
        if not file_path:
            # Create a demo document if no path provided
            demo_text = """
            Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design. 
            Built by experienced developers, it takes care of much of the hassle of web development, so you can focus 
            on writing your app without needing to reinvent the wheel. It's free and open source.
            
            Django's primary goal is to ease the creation of complex, database-driven websites. 
            The framework emphasizes reusability and "pluggability" of components, less code, low coupling, 
            rapid development, and the principle of don't repeat yourself (DRY).
            
            Python is used throughout, even for settings, files, and data models. 
            Django also provides an optional administrative create, read, update and delete interface 
            that is generated dynamically through introspection and configured via admin models.
            """
            
            # Create a demo file
            demo_path = os.path.join(settings.BASE_DIR, 'demo_document.txt')
            with open(demo_path, 'w', encoding='utf-8') as f:
                f.write(demo_text)
            file_path = demo_path
            self.stdout.write(f"Created demo document at: {demo_path}")
        
        # Read the file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error reading file {file_path}: {str(e)}")
            )
            return
        
        # Index the document
        self.stdout.write(f"Indexing document: {title}")
        document = index_document(title, text_content)
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully indexed document '{title}' with ID: {document.id}\n"
                f"Text length: {len(text_content)} characters"
            )
        )
        
        # Show stats
        from chat.rag_service import get_index_stats
        stats = get_index_stats()
        self.stdout.write(f"Index stats: {stats}")