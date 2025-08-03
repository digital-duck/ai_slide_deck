#!/usr/bin/env python3
"""
Prefect Slide Deck Generator - Distributed Design
Generates navigation index and discovers existing slide files
"""

import os
import json
from pathlib import Path
import re

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

def create_slide_template(title, content, section=None):
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

def discover_slides(slides_dir):
    """Discover all slide files and extract metadata"""
    slides = []
    slide_pattern = re.compile(r'^(\d{3})-(.+)\.html$')
    
    # Get all HTML files that match the pattern
    html_files = [f for f in os.listdir(slides_dir) if f.endswith('.html') and f != 'index.html']
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
                print(f"Warning: Could not read {filename}: {e}")
                # Fallback to derived info
                slides.append({
                    'number': number,
                    'title': title,
                    'filename': filename,
                    'section': "Appendix" if int(number) > 10 else "Main"
                })
    
    return slides

def create_navigation_html(slides, slides_dir):
    """Create the main navigation HTML"""
    # Create sidebar items
    sidebar_items = []
    current_section = None
    
    for i, slide in enumerate(slides):
        section = slide['section']
        
        if section != current_section:
            if current_section is not None:
                sidebar_items.append('</div>')
            sidebar_items.append(f'<div class="section"><h3>{section}</h3>')
            current_section = section
        
        active_class = "active" if i == 0 else ""
        sidebar_items.append(f'''
            <div class="slide-item {active_class}" onclick="loadSlide('{slide["filename"]}', {i})">
                {slide["number"]}. {slide["title"]}
            </div>
        ''')
    
    if current_section is not None:
        sidebar_items.append('</div>')
    
    sidebar_html = ''.join(sidebar_items)
    
    # Get first slide filename for initial load
    first_slide = slides[0]['filename'] if slides else 'index.html'
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prefect Slide Deck</title>
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
            <h2>🚀 Prefect Slides</h2>
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
            </div>
        </div>
    </div>
    
    <script>
        const slides = {json.dumps([slide['filename'] for slide in slides])};
        let currentSlideIndex = 0;
        
        function loadSlide(filename, index) {{
            document.getElementById('slide-frame').src = filename;
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
    </script>
</body>
</html>'''

def create_sample_slides(slides_dir):
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
        
        print(f"Created sample slide: {filename}")

def generate_slide_deck():
    """Main function to generate navigation and discover slides"""
    slides_dir = Path("prefect_slides")
    slides_dir.mkdir(exist_ok=True)
    
    # Check if slides exist, if not create samples
    existing_slides = [f for f in os.listdir(slides_dir) if f.endswith('.html') and f != 'index.html']
    
    if not existing_slides:
        print("No slides found. Creating sample slides...")
        create_sample_slides(slides_dir)
    
    # Discover all slides
    slides = discover_slides(slides_dir)
    
    if not slides:
        print("No valid slides found in the directory!")
        return
    
    print(f"Discovered {len(slides)} slides:")
    for slide in slides:
        print(f"  {slide['number']}. {slide['title']} ({slide['section']})")
    
    # Generate navigation index
    index_filepath = slides_dir / "index.html"
    navigation_html = create_navigation_html(slides, slides_dir)
    
    with open(index_filepath, 'w', encoding='utf-8') as f:
        f.write(navigation_html)
    
    print(f"\nGenerated navigation: index.html")
    print(f"Open {slides_dir}/index.html in your browser to view the presentation.")
    
    return f"Generated navigation for {len(slides)} slides in '{slides_dir}' directory"

def save_slide_metadata(slides_dir):
    """Save slide metadata to JSON for easy reference"""
    slides = discover_slides(slides_dir)
    
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
    
    metadata_file = slides_dir / 'slides_metadata.json'
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Saved metadata to: {metadata_file}")

if __name__ == "__main__":
    slides_dir = Path("prefect_slides")
    
    # Generate the navigation
    result = generate_slide_deck()
    print(result)
    
    # Save metadata
    save_slide_metadata(slides_dir)
    
    print("\n📋 Usage:")
    print("1. Add individual slide HTML files following the pattern: XXX-slide-title.html")
    print("2. Run this script to regenerate navigation")
    print("3. Slides numbered 001-010 are 'Main', 011+ are 'Appendix'")
    print("4. Use the create_slide_template() function to maintain consistent styling")
