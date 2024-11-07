import os
import requests
import markdown
from configparser import ConfigParser
from collections import defaultdict

# GitHub base URL for projects
GITHUB_BASE_URL = "https://raw.githubusercontent.com/cpp-toolbox"

def read_projects_from_file(filename):
    """Read project names from a text file, each project on a new line."""
    with open(filename, "r") as file:
        projects = [line.strip() for line in file if line.strip()]
    return projects

def fetch_file(url):
    """Fetch file content from a URL, handling missing files gracefully."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException:
        print(f"Error: Could not fetch file at {url}")
        return None

def markdown_to_html(md_content):
    """Convert Markdown content to HTML."""
    return markdown.markdown(md_content)

def parse_sbpt_ini(ini_content):
    """Parse sbpt.ini content and retrieve dependencies and tags."""
    config = ConfigParser()
    config.read_string(ini_content)
    
    dependencies = []
    tags = []
    
    if 'subproject' in config:
        # Get dependencies as a list
        dependencies = [dep.strip() for dep in config['subproject'].get('dependencies', '').split(',') if dep.strip()]
        # Get tags as a list
        tags = [tag.strip() for tag in config['subproject'].get('tags', '').split(',') if tag.strip()]
    
    return dependencies, tags

def create_html(project_name, md_html, dependencies):
    """Generate HTML content with dependencies linked and stylesheet included."""
    # GitHub URL for the project
    github_url = f"https://github.com/cpp-toolbox/{project_name}"
    
    # Add the stylesheet link and title with GitHub link, relative because github pages bad with /project/index.html takes you back out...
    html_content = f'<link rel="stylesheet" href="../cjm-css/styles.css">\n'
    html_content += f'<title>{project_name} - GitHub</title>\n'
    html_content += f'<div class="wrapper">\n'
    
    # Add the markdown content converted to HTML
    html_content += md_html
    
    html_content += f"\n<h2><a href='{github_url}'>source code</a></h2>\n"

    # Add dependencies list if any
    if dependencies:
        html_content += "\n<h2>subproject dependencies</h2>\n<ul>\n"
        for dep in dependencies:
            dep_link = f"{dep}.html"
            html_content += f'\t<li><a href="{dep_link}">{dep}</a></li>\n'
        html_content += "</ul>\n"
    
    # Close the wrapper div
    html_content += "</div>\n"
    
    return html_content

def save_html(filename, html_content):
    """Save HTML content to a file."""
    with open(filename, "w") as file:
        file.write(html_content)
    print(f"Saved HTML as {filename}")

def generate_index_html(tagged_projects):
    """Generate an index HTML file based on tags."""
    index_content = '<link rel="stylesheet" href="/cjm-css/styles.css">\n'
    index_content += '<div class="wrapper">\n'
    index_content += "<h1>Project Index by Tag</h1>\n"
    
    for tag, projects in sorted(tagged_projects.items()):
        index_content += f"<h2>{tag}</h2>\n<ul>\n"
        for project in sorted(projects):
            project_link = f"{project}.html"
            index_content += f'\t<li><a href="{project_link}">{project}</a></li>\n'
        index_content += "</ul>\n"
    
    index_content += "</div>\n"  # Close the wrapper div
    save_html("index.html", index_content)

def main():
    # Read projects from subprojects.txt
    projects = read_projects_from_file("subprojects.txt")
    tagged_projects = defaultdict(list)  # Dictionary to store tags and associated projects
    
    for project in projects:
        print(f"\nProcessing project: {project}")

        # Fetch README.md or readme.md
        readme_url = f"{GITHUB_BASE_URL}/{project}/main/README.md"
        md_content = fetch_file(readme_url)
        if not md_content:
            readme_url = f"{GITHUB_BASE_URL}/{project}/main/readme.md"
            md_content = fetch_file(readme_url)
        
        # Convert Markdown to HTML if content was found
        md_html = markdown_to_html(md_content) if md_content else "<p>Error: README file not found.</p>"

        # Fetch and parse sbpt.ini
        sbpt_ini_url = f"{GITHUB_BASE_URL}/{project}/main/sbpt.ini"
        sbpt_ini_content = fetch_file(sbpt_ini_url)
        
        if sbpt_ini_content:
            dependencies, tags = parse_sbpt_ini(sbpt_ini_content)
        else:
            dependencies, tags = [], []
        
        # Assign project to tags, or to 'Unsorted' if no tags
        if tags:
            for tag in tags:
                tagged_projects[tag].append(project)
        else:
            tagged_projects["Unsorted"].append(project)
        
        # Create HTML with dependencies
        html_content = create_html(project, md_html, dependencies)
        
        # Save HTML to a file
        save_html(f"{project}.html", html_content)

    # Generate index.html based on tags
    generate_index_html(tagged_projects)

if __name__ == "__main__":
    main()
