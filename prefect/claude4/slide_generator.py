#!/usr/bin/env python3
"""
Enhanced Prefect Slide Deck Generator with Click CLI and PDF Export
Generates navigation index from existing slide files with customizable options
"""

import os
import json
import click
from pathlib import Path
import re
from typing import List, Dict, Optional
import asyncio
import tempfile
import shutil

# Optional imports for PDF generation
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

def create_base_styles():
    """Create the base CSS styles for slides"""
    return '''
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .slide-container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            padding: 40px;
            min-height: 600px;
        }
        
        h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 30px;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
        }
        
        h2 {
            color: #34495e;
            font-size: 1.8em;
            margin-bottom: 20px;
            text-align: center;
        }
        
        h3 {
            color: #2980b9;
            font-size: 1.4em;
            margin: 25px 0 15px 0;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }
        
        h4 {
            color: #8e44ad;
            font-size: 1.2em;
            margin: 20px 0 10px 0;
        }
        
        .slide-content {
            font-size: 1.1em;
        }
        
        ul {
            margin: 15px 0 15px 30px;
        }
        
        li {
            margin: 8px 0;
        }
        
        .two-column {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin: 20px 0;
        }
        
        .column {
            padding: 0 10px;
        }
        
        .code-block {
            background: #2c3e50;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            overflow-x: auto;
        }
        
        .code-block pre {
            color: #ecf0f1;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.4;
        }
        
        .code-block code {
            color: #ecf0f1;
        }
        
        .highlight-box {
            background: linear-gradient(135deg, #74b9ff, #0984e3);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
            font-weight: 500;
        }
        
        .comparison-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 0.95em;
        }
        
        .comparison-table th {
            background: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        
        .comparison-table td {
            padding: 12px;
            border-bottom: 1px solid #ddd;
            vertical-align: top;
        }
        
        .comparison-table tr:nth-child(even) {
            background: #f8f9fa;
        }
        
        .comparison-table tr:hover {
            background: #e3f2fd;
        }
        
        strong {
            color: #2c3e50;
        }
        
        em {
            color: #7f8c8d;
            font-style: italic;
        }
        
        p {
            margin: 10px 0;
        }
        
        @media (max-width: 768px) {
            .slide-container {
                padding: 20px;
                margin: 10px;
            }
            
            .two-column {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            
            h1 {
                font-size: 2em;
            }
            
            .code-block {
                font-size: 0.8em;
            }
        }
    </style>
    '''

def create_slide_template(title: str, content: str, section: Optional[str] = None) -> str:
    """Create a basic slide HTML template"""
    section_badge = ""
    if section:
        section_badge = f'<div style="background: #e74c3c; color: white; padding: 5px 15px; border-radius: 20px; display: inline-block; margin-bottom: 20px; font-size: 0.9em;">{section}</div>'
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {create_base_styles()}
</head>
<body>
    <div class="slide-container">
        {section_badge}
        {content}
    </div>
</body>
</html>'''

def discover_slides(slides_dir: Path) -> List[Dict]:
    """Discover all slide files and extract metadata"""
    slides = []
    slide_pattern = re.compile(r'^(\d{3})-(.+)\.html$')
    
    if not slides_dir.exists():
        click.echo(f"❌ Directory {slides_dir} does not exist!", err=True)
        return []
    
    # Get all HTML files that match the pattern
    html_files = [f for f in os.listdir(slides_dir) if f.endswith('.html') and f != 'index.html']
    
    if not html_files:
        click.echo(f"⚠️  No HTML files found in {slides_dir}", err=True)
        return []
    
    html_files.sort()  # Sort by filename
    
    for filename in html_files:
        match = slide_pattern.match(filename)
        if match:
            number = match.group(1)
            title_slug = match.group(2)
            
            # Convert slug back to title
            title = title_slug.replace('-', ' ').replace('and', '&').title()
            
            # Read the file to extract actual title and section
            filepath = slides_dir / filename
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract title from HTML
                title_match = re.search(r'<title>.*?-\s*(.+?)</title>', content)
                if title_match:
                    title = title_match.group(1)
                
                # Check if it's an appendix slide
                section = "Appendix" if "Appendix" in content else "Main"
                
                slides.append({
                    'number': number,
                    'title': title,
                    'filename': filename,
                    'section': section
                })
                
            except Exception as e:
                click.echo(f"⚠️  Warning: Could not read {filename}: {e}", err=True)
                # Fallback to derived info
                slides.append({
                    'number': number,
                    'title': title,
                    'filename': filename,
                    'section': "Appendix" if int(number) > 10 else "Main"
                })
        else:
            click.echo(f"⚠️  Skipping {filename} - doesn't match pattern XXX-title.html")
    
    return slides

def create_navigation_html(slides: List[Dict], page_title: str, slides_dir: Path) -> str:
    """Create the main navigation HTML"""
    # Create sidebar items
    sidebar_items = []
    current_section = None
    
    # Determine relative path from navigation file to slides directory
    slides_dir_name = slides_dir.name if slides_dir.name != '.' else ''
    slides_path_prefix = f"{slides_dir_name}/" if slides_dir_name else ""
    
    for i, slide in enumerate(slides):
        section = slide['section']
        
        if section != current_section:
            if current_section is not None:
                sidebar_items.append('</div>')
            sidebar_items.append(f'<div class="section"><h3>{section}</h3>')
            current_section = section
        
        active_class = "active" if i == 0 else ""
        slide_path = f"{slides_path_prefix}{slide['filename']}"
        sidebar_items.append(f'''
            <div class="slide-item {active_class}" onclick="loadSlide('{slide_path}', {i})">
                {slide["number"]}. {slide["title"]}
            </div>
        ''')
    
    if current_section is not None:
        sidebar_items.append('</div>')
    
    sidebar_html = ''.join(sidebar_items)
    
    # Get first slide filename for initial load with proper path
    first_slide = f"{slides_path_prefix}{slides[0]['filename']}" if slides else 'index.html'
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f6fa;
            height: 100vh;
            overflow: hidden;
        }}
        
        .container {{
            display: flex;
            height: 100vh;
        }}
        
        .sidebar {{
            width: 300px;
            background: #2c3e50;
            color: white;
            overflow-y: auto;
            padding: 20px 0;
        }}
        
        .sidebar h2 {{
            text-align: center;
            padding: 0 20px 20px 20px;
            border-bottom: 2px solid #34495e;
            margin-bottom: 20px;
            color: #ecf0f1;
            font-size: 1.2em;
        }}
        
        .section h3 {{
            background: #34495e;
            padding: 10px 20px;
            margin: 10px 0 5px 0;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .slide-item {{
            padding: 12px 20px;
            cursor: pointer;
            transition: background-color 0.3s;
            border-left: 4px solid transparent;
            font-size: 0.9em;
        }}
        
        .slide-item:hover {{
            background: #34495e;
        }}
        
        .slide-item.active {{
            background: #3498db;
            border-left-color: #2980b9;
            font-weight: 600;
        }}
        
        .main-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
        }}
        
        .slide-frame {{
            flex: 1;
            border: none;
            background: white;
        }}
        
        .navigation {{
            background: white;
            padding: 15px 30px;
            border-top: 1px solid #ddd;
            display: flex;
            justify-content: center;
            gap: 15px;
        }}
        
        .nav-btn {{
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: background-color 0.3s;
        }}
        
        .nav-btn:hover:not(:disabled) {{
            background: #2980b9;
        }}
        
        .nav-btn:disabled {{
            background: #bdc3c7;
            cursor: not-allowed;
        }}
        
        .pdf-btn {{
            background: #e74c3c !important;
            margin-left: 10px;
        }}
        
        .pdf-btn:hover {{
            background: #c0392b !important;
        }}
        
        #pdf-status {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 20px;
            border-radius: 10px;
            display: none;
            z-index: 1000;
        }}
        
        .slide-counter {{
            background: #ecf0f1;
            padding: 10px 20px;
            text-align: center;
            color: #2c3e50;
            font-weight: 600;
            border-bottom: 1px solid #ddd;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                flex-direction: column;
            }}
            
            .sidebar {{
                width: 100%;
                height: 200px;
            }}
            
            .navigation {{
                padding: 10px 15px;
                gap: 10px;
            }}
            
            .nav-btn {{
                padding: 8px 15px;
                font-size: 14px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h2>🚀 {page_title}</h2>
            {sidebar_html}
        </div>
        
        <div class="main-content">
            <div class="slide-counter">
                <span id="current-slide">1</span> / {len(slides)}
            </div>
            
            <iframe id="slide-frame" class="slide-frame" src="{first_slide}"></iframe>
            
            <div class="navigation">
                <button class="nav-btn" id="first-btn" onclick="goToSlide(0)">&lt;&lt;</button>
                <button class="nav-btn" id="prev-btn" onclick="previousSlide()">&lt;</button>
                <button class="nav-btn" id="next-btn" onclick="nextSlide()">&gt;</button>
                <button class="nav-btn" id="last-btn" onclick="goToSlide({len(slides) - 1})">&gt;&gt;</button>
                <button class="nav-btn pdf-btn" id="pdf-btn" onclick="generatePDF()" title="Generate PDF">📄 PDF</button>
            </div>
        </div>
    </div>
    
    <!-- PDF Generation Status -->
    <div id="pdf-status">
        <div id="pdf-message">Generating PDF...</div>
        <div style="text-align: center; margin-top: 10px;">
            <div style="display: inline-block; width: 20px; height: 20px; border: 2px solid #f3f3f3; border-top: 2px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite;"></div>
        </div>
    </div>
    
    <style>
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
    
    <script>
        const slides = {json.dumps([f"{slides_path_prefix}{slide['filename']}" for slide in slides])};
        const slideFilenames = {json.dumps([slide['filename'] for slide in slides])};
        let currentSlideIndex = 0;
        
        function loadSlide(slidePathWithPrefix, index) {{
            document.getElementById('slide-frame').src = slidePathWithPrefix;
            currentSlideIndex = index;
            updateUI();
        }}
        
        function updateUI() {{
            // Update slide counter
            document.getElementById('current-slide').textContent = currentSlideIndex + 1;
            
            // Update active sidebar item
            document.querySelectorAll('.slide-item').forEach((item, index) => {{
                item.classList.toggle('active', index === currentSlideIndex);
            }});
            
            // Update navigation buttons
            document.getElementById('first-btn').disabled = currentSlideIndex === 0;
            document.getElementById('prev-btn').disabled = currentSlideIndex === 0;
            document.getElementById('next-btn').disabled = currentSlideIndex === slides.length - 1;
            document.getElementById('last-btn').disabled = currentSlideIndex === slides.length - 1;
        }}
        
        function goToSlide(index) {{
            if (index >= 0 && index < slides.length) {{
                loadSlide(slides[index], index);
            }}
        }}
        
        function nextSlide() {{
            if (currentSlideIndex < slides.length - 1) {{
                goToSlide(currentSlideIndex + 1);
            }}
        }}
        
        function previousSlide() {{
            if (currentSlideIndex > 0) {{
                goToSlide(currentSlideIndex - 1);
            }}
        }}
        
        // Keyboard navigation
        document.addEventListener('keydown', function(e) {{
            switch(e.key) {{
                case 'ArrowLeft':
                    previousSlide();
                    break;
                case 'ArrowRight':
                    nextSlide();
                    break;
                case 'Home':
                    goToSlide(0);
                    break;
                case 'End':
                    goToSlide(slides.length - 1);
                    break;
            }}
        }});
        
        // Initialize
        updateUI();
        
        // PDF Generation Function
        async function generatePDF() {{
            const pdfStatus = document.getElementById('pdf-status');
            const pdfMessage = document.getElementById('pdf-message');
            
            try {{
                pdfStatus.style.display = 'block';
                pdfMessage.textContent = 'Preparing PDF generation...';
                
                // Call the PDF generation endpoint
                const response = await fetch('/generate-pdf', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        slides: slideFilenames,
                        title: '{page_title}'
                    }})
                }});
                
                if (response.ok) {{
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = '{page_title.lower().replace(" ", "_")}_slides.pdf';
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    
                    pdfMessage.textContent = 'PDF downloaded successfully!';
                    setTimeout(() => {{
                        pdfStatus.style.display = 'none';
                    }}, 2000);
                }} else {{
                    throw new Error('PDF generation failed');
                }}
            }} catch (error) {{
                console.error('PDF generation error:', error);
                pdfMessage.textContent = 'PDF generation failed. Please try the CLI command instead.';
                setTimeout(() => {{
                    pdfStatus.style.display = 'none';
                }}, 3000);
            }}
        }}
    </script>
</body>
</html>'''

def save_slide_metadata(slides: List[Dict], output_dir: Path) -> None:
    """Save slide metadata to JSON for easy reference"""
    metadata = {
        'total_slides': len(slides),
        'slides': slides,
        'sections': {}
    }
    
    # Group by section
    for slide in slides:
        section = slide['section']
        if section not in metadata['sections']:
            metadata['sections'][section] = []
        metadata['sections'][section].append(slide)
    
    metadata_file = output_dir / 'slides_metadata.json'
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    click.echo(f"📄 Saved metadata to: {metadata_file}")

async def generate_pdf_playwright(slides_dir: Path, slides: List[Dict], output_file: Path, page_title: str) -> None:
    """Generate PDF using Playwright (recommended method)"""
    if not PLAYWRIGHT_AVAILABLE:
        raise ImportError("Playwright not available. Install with: pip install playwright && playwright install")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        click.echo("🖨️  Generating PDF pages...")
        
        # Create a combined HTML document with all slides
        combined_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{page_title}</title>
            <style>
                @page {{
                    size: A4;
                    margin: 0.5in;
                }}
                .slide-page {{
                    page-break-after: always;
                    min-height: 100vh;
                }}
                .slide-page:last-child {{
                    page-break-after: avoid;
                }}
                body {{
                    margin: 0;
                    padding: 0;
                }}
            </style>
        </head>
        <body>
        """
        
        for i, slide in enumerate(slides):
            slide_path = slides_dir / slide['filename']
            
            if not slide_path.exists():
                click.echo(f"⚠️  Warning: {slide_path} not found, skipping...")
                continue
            
            click.echo(f"   Processing slide {i+1}/{len(slides)}: {slide['title']}")
            
            # Read slide content
            with open(slide_path, 'r', encoding='utf-8') as f:
                slide_content = f.read()
            
            # Extract the slide container content
            container_match = re.search(r'<div class="slide-container"[^>]*>(.*?)</div>\s*</body>', slide_content, re.DOTALL)
            if container_match:
                slide_body = container_match.group(1)
                
                # Add slide to combined HTML
                combined_html += f"""
                <div class="slide-page">
                    <div class="slide-container" style="
                        max-width: 1000px;
                        margin: 0 auto;
                        background: white;
                        border-radius: 15px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                        padding: 40px;
                        min-height: 600px;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                    ">
                        {slide_body}
                    </div>
                </div>
                """
            else:
                click.echo(f"⚠️  Warning: Could not extract content from {slide['filename']}")
        
        combined_html += """
        </body>
        </html>
        """
        
        # Generate PDF from combined HTML
        await page.set_content(combined_html)
        await page.wait_for_load_state('networkidle')
        
        # Generate single PDF with all slides
        pdf_bytes = await page.pdf(
            format='A4',
            margin={
                'top': '0.5in',
                'bottom': '0.5in',
                'left': '0.5in',
                'right': '0.5in'
            },
            print_background=True,
            prefer_css_page_size=True
        )
        
        await browser.close()
        
        # Save the complete PDF
        with open(output_file, 'wb') as f:
            f.write(pdf_bytes)
        
        click.echo(f"✅ PDF generated with {len(slides)} slides: {output_file}")

async def generate_pdf_playwright_alternative(slides_dir: Path, slides: List[Dict], output_file: Path, page_title: str) -> None:
    """Alternative Playwright method: Generate individual PDFs and merge using PyPDF2"""
    if not PLAYWRIGHT_AVAILABLE:
        raise ImportError("Playwright not available. Install with: pip install playwright && playwright install")
    
    try:
        from PyPDF2 import PdfWriter, PdfReader
        import io
        PYPDF2_AVAILABLE = True
    except ImportError:
        PYPDF2_AVAILABLE = False
        # Fall back to single HTML method
        await generate_pdf_playwright(slides_dir, slides, output_file, page_title)
        return
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        click.echo("🖨️  Generating individual PDF pages...")
        
        pdf_writer = PdfWriter()
        
        for i, slide in enumerate(slides):
            slide_path = slides_dir / slide['filename']
            
            if not slide_path.exists():
                click.echo(f"⚠️  Warning: {slide_path} not found, skipping...")
                continue
            
            click.echo(f"   Processing slide {i+1}/{len(slides)}: {slide['title']}")
            
            # Navigate to slide
            await page.goto(f"file://{slide_path.absolute()}")
            await page.wait_for_load_state('networkidle')
            
            # Generate PDF for this slide
            pdf_bytes = await page.pdf(
                format='A4',
                margin={
                    'top': '0.5in',
                    'bottom': '0.5in',
                    'left': '0.5in',
                    'right': '0.5in'
                },
                print_background=True,
                prefer_css_page_size=True
            )
            
            # Add to PDF writer
            pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
            for page_num in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page_num])
        
        await browser.close()
        
        # Write combined PDF
        with open(output_file, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)
        
        click.echo(f"✅ PDF generated with {len(slides)} slides: {output_file}")

async def generate_pdf_with_method(method: str, slides_dir: Path, slides: List[Dict], output_file: Path, page_title: str) -> None:
    """Generate PDF using specified method"""
    if method == "playwright":
        await generate_pdf_playwright(slides_dir, slides, output_file, page_title)
    elif method == "playwright-merge":
        await generate_pdf_playwright_alternative(slides_dir, slides, output_file, page_title)
    elif method == "weasyprint":
        generate_pdf_weasyprint(slides_dir, slides, output_file, page_title)
    else:
        raise ValueError(f"Unknown PDF generation method: {method}")

@click.command()
@click.option(
    '--slides-dir',
    '-d',
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help='Directory containing HTML slide files'
)
@click.option(
    '--output',
    '-o',
    type=click.Path(path_type=Path),
    default=None,
    help='Output PDF file path (default: <title>_slides.pdf)'
)
@click.option(
    '--title',
    '-t',
    default='Slides',
    help='Title for the PDF document'
)
@click.option(
    '--method',
    '-m',
    type=click.Choice(['playwright', 'playwright-merge', 'weasyprint']),
    default='playwright',
    help='PDF generation method (default: playwright)'
)
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    help='Verbose output'
)
def generate_pdf_command(
    slides_dir: Path,
    output: Optional[Path],
    title: str,
    method: str,
    verbose: bool
) -> None:
    """
    Generate PDF from HTML slide files.
    
    This command converts all HTML slides in a directory to a single PDF document.
    
    Examples:
    
        # Basic usage
        python slide_generator.py generate-pdf -d prefect_slides
        
        # Custom output and title
        python slide_generator.py generate-pdf -d slides -o presentation.pdf -t "My Presentation"
        
        # Use WeasyPrint instead of Playwright
        python slide_generator.py generate-pdf -d slides -m weasyprint
    """
    
    # Setup output path
    if output is None:
        safe_title = title.lower().replace(' ', '_').replace('/', '_')
        output = Path(f"{safe_title}_slides.pdf")
    
    if verbose:
        click.echo(f"🔍 Slides directory: {slides_dir}")
        click.echo(f"📄 Output PDF: {output}")
        click.echo(f"🔧 Method: {method}")
        click.echo(f"📝 Title: {title}")
    
    # Check method availability
    if method == "playwright" and not PLAYWRIGHT_AVAILABLE:
        click.echo("❌ Playwright not installed. Install with:")
        click.echo("   pip install playwright")
        click.echo("   playwright install")
        return
    
    if method == "weasyprint" and not WEASYPRINT_AVAILABLE:
        click.echo("❌ WeasyPrint not installed. Install with:")
        click.echo("   pip install weasyprint")
        return
    
    # Discover slides
    slides = discover_slides(slides_dir)
    
    if not slides:
        click.echo(f"❌ No valid slides found in {slides_dir}")
        return
    
    click.echo(f"📊 Found {len(slides)} slides")
    
    try:
        # Generate PDF
        if method == "playwright":
            asyncio.run(generate_pdf_with_method(method, slides_dir, slides, output, title))
        else:
            asyncio.run(generate_pdf_with_method(method, slides_dir, slides, output, title))
        
        file_size = output.stat().st_size / (1024 * 1024)  # MB
        click.echo(f"🎉 Success! PDF generated: {output} ({file_size:.1f} MB)")
        
    except Exception as e:
        click.echo(f"❌ PDF generation failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()

def create_sample_slides(slides_dir: Path) -> None:
    """Create a few sample slides to demonstrate the structure"""
    sample_slides = [
        {
            'number': '001',
            'title': 'Introduction to Prefect',
            'content': '''
            <h1>🚀 Prefect</h1>
            <h2>Modern Workflow Orchestration</h2>
            <div class="slide-content">
                <ul>
                    <li><strong>What is Prefect?</strong> A modern workflow orchestration platform</li>
                    <li><strong>Purpose:</strong> Build, run, and monitor data pipelines at scale</li>
                    <li><strong>Philosophy:</strong> "Negative engineering" - eliminate workflow failures</li>
                    <li><strong>Key Focus:</strong> Developer experience and operational simplicity</li>
                </ul>
                <div class="highlight-box">
                    <p><em>"The easiest way to coordinate your data stack"</em></p>
                </div>
            </div>
            '''
        },
        {
            'number': '002',
            'title': 'Quick Setup',
            'content': '''
            <h1>⚡ Quick Setup</h1>
            <div class="slide-content">
                <h3>1. Installation</h3>
                <div class="code-block">
                    <pre><code># Install Prefect
pip install prefect

# Or with extras
pip install "prefect[dev,kubernetes]"</code></pre>
                </div>
                
                <h3>2. First Flow</h3>
                <div class="code-block">
                    <pre><code>from prefect import flow, task

@task
def say_hello(name: str) -> str:
    return f"Hello, {name}!"

@flow
def hello_world():
    greeting = say_hello("Prefect")
    print(greeting)

if __name__ == "__main__":
    hello_world()</code></pre>
                </div>
            </div>
            '''
        },
        {
            'number': '011',
            'title': 'Prefect vs Airflow',
            'section': 'Appendix',
            'content': '''
            <h1>🆚 Prefect vs Apache Airflow</h1>
            <div class="slide-content">
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>Aspect</th>
                            <th>Prefect</th>
                            <th>Apache Airflow</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Philosophy</strong></td>
                            <td>Negative engineering, eliminate failures</td>
                            <td>Workflow-as-code, maximum control</td>
                        </tr>
                        <tr>
                            <td><strong>Dynamic Workflows</strong></td>
                            <td>✅ Native support</td>
                            <td>⚠️ Limited, requires workarounds</td>
                        </tr>
                        <tr>
                            <td><strong>Learning Curve</strong></td>
                            <td>🟢 Gentle, Pythonic</td>
                            <td>🔴 Steep, many concepts</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            '''
        }
    ]
    
    for slide in sample_slides:
        filename = f"{slide['number']}-{slide['title'].lower().replace(' ', '-').replace('&', 'and')}.html"
        filepath = slides_dir / filename
        
        html_content = create_slide_template(
            f"{slide['number']} - {slide['title']}", 
            slide['content'],
            slide.get('section')
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        click.echo(f"📄 Created sample slide: {filename}")

@click.command()
@click.option(
    '--slides-dir',
    '-d',
    type=click.Path(exists=False, path_type=Path),
    default='prefect_slides',
    help='Directory containing HTML slide files (default: prefect_slides)'
)
@click.option(
    '--title',
    '-t',
    default='Prefect Slides',
    help='Title for the HTML page (default: "Prefect Slides")'
)
@click.option(
    '--output',
    '-o',
    type=click.Path(path_type=Path),
    default=None,
    help='Output navigation HTML file path (default: <slides-dir>/index.html)'
)
@click.option(
    '--create-samples',
    is_flag=True,
    help='Create sample slides if directory is empty'
)
@click.option(
    '--metadata',
    is_flag=True,
    help='Generate slides metadata JSON file'
)
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    help='Verbose output'
)
def generate_navigation(
    slides_dir: Path,
    title: str,
    output: Optional[Path],
    create_samples: bool,
    metadata: bool,
    verbose: bool
) -> None:
    """
    Generate navigation HTML from slide files.
    
    This tool discovers HTML slide files following the pattern XXX-title.html
    and generates a navigation interface with sidebar and controls.
    
    Example usage:
    
        # Basic usage with defaults
        python slide_generator.py
        
        # Custom directory and title
        python slide_generator.py -d my_slides -t "My Presentation"
        
        # Custom output file
        python slide_generator.py -o navigation.html
        
        # Create samples if directory is empty
        python slide_generator.py --create-samples
    """
    
    # Setup output path
    if output is None:
        output = slides_dir / 'index.html'
    
    # Ensure slides directory exists
    slides_dir.mkdir(exist_ok=True)
    
    if verbose:
        click.echo(f"🔍 Looking for slides in: {slides_dir}")
        click.echo(f"📝 Page title: {title}")
        click.echo(f"📄 Output file: {output}")
    
    # Check if slides exist, create samples if requested and directory is empty
    existing_slides = [f for f in os.listdir(slides_dir) if f.endswith('.html') and f != 'index.html']
    
    if not existing_slides and create_samples:
        click.echo("📝 No slides found. Creating sample slides...")
        create_sample_slides(slides_dir)
    
    # Discover all slides
    slides = discover_slides(slides_dir)
    
    if not slides:
        click.echo("❌ No valid slides found! Use --create-samples to generate examples.", err=True)
        click.echo("\n💡 Expected pattern: XXX-slide-title.html (e.g., 001-introduction.html)")
        return
    
    if verbose:
        click.echo(f"\n📊 Discovered {len(slides)} slides:")
        for slide in slides:
            click.echo(f"  {slide['number']}. {slide['title']} ({slide['section']})")
    
    # Generate navigation index
    navigation_html = create_navigation_html(slides, title, slides_dir)
    
    with open(output, 'w', encoding='utf-8') as f:
        f.write(navigation_html)
    
    click.echo(f"\n✅ Generated navigation: {output}")
    
    # Save metadata if requested
    if metadata:
        save_slide_metadata(slides, slides_dir)
    
    # Success message
    click.echo(f"\n🚀 Success! Open {output} in your browser to view the presentation.")
    click.echo(f"📋 Found {len(slides)} slides total")
    
    # Show section breakdown
    sections = {}
    for slide in slides:
        section = slide['section']
        sections[section] = sections.get(section, 0) + 1
    
    for section, count in sections.items():
        click.echo(f"   • {section}: {count} slides")

@click.group()
def cli():
    """Prefect Slide Deck Generator with Click CLI"""
    pass

@cli.command()
@click.argument('title')
@click.argument('content_file', type=click.File('r'))
@click.option('--number', '-n', required=True, help='Slide number (e.g., 001)')
@click.option('--section', '-s', help='Section name (e.g., Appendix)')
@click.option('--output-dir', '-d', type=click.Path(path_type=Path), default='prefect_slides')
def create_slide(title: str, content_file, number: str, section: Optional[str], output_dir: Path):
    """Create a new slide from content file"""
    content = content_file.read()
    
    # Ensure 3-digit number format
    number = f"{int(number):03d}"
    
    # Generate filename
    filename = f"{number}-{title.lower().replace(' ', '-').replace('&', 'and')}.html"
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Generate HTML
    html_content = create_slide_template(f"{number} - {title}", content, section)
    
    # Write file
    filepath = output_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    click.echo(f"✅ Created slide: {filepath}")

# Add the generate command to the CLI group
cli.add_command(generate_navigation, name='generate')
cli.add_command(generate_pdf_command, name='generate-pdf')

if __name__ == "__main__":
    cli()
