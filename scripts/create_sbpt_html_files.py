import os
import requests
import markdown
from typing import List
from configparser import ConfigParser
from collections import defaultdict
from fs_utils.main import get_absolute_path_of_where_this_script_exists
from fsweb.html_utils.main import  BLANK_HTML_FILE, add_text_to_header_and_body_of_html

# GitHub base URL for projects
GITHUB_BASE_URL = "https://raw.githubusercontent.com/cpp-toolbox"

def get_projects_from_file(filename: str) -> List[str]:
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
    html = markdown.markdown(
        md_content,
        extensions=['fenced_code', 'codehilite']
    )
    return html

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
    ssh_url = f"git@github.com:cpp-toolbox/{project_name}.git"
    html_header_content = ""
    html_body_content = ""
    
    # Add the markdown content converted to HTML
    html_body_content += md_html
    
    html_body_content += f"\n<h2><a href='{github_url}'>source code</a></h2>\n"
    html_body_content += f"\n<h2>git submodule add --recurse-submodules {ssh_url}</h2>\n"

    # Add dependencies list if any
    if dependencies:
        html_body_content += "\n<h2>subproject dependencies</h2>\n<ul>\n"
        for dep in dependencies:
            dep_link = f"{dep}.html"
            html_body_content += f'\t<li><a href="{dep_link}">{dep}</a></li>\n'
        html_body_content += "</ul>\n"

    return add_text_to_header_and_body_of_html(BLANK_HTML_FILE, html_header_content, html_body_content)

def save_html(save_dir, filename, html_content):
    """Save HTML content to a file."""
    filepath = save_dir + "/" + filename
    with open(filepath , "w") as file:
        file.write(html_content)
    print(f"Saved HTML as {filepath }")

def generate_index_html(subproject_directory, tagged_projects):
    """Generate an index HTML file based on tags, ensuring 'unsorted' comes last."""
    index_header_content = '<link rel="stylesheet" href="../cjm-css/styles.css">\n'
    index_body_content = ""
    index_body_content += '<div class="wrapper">\n'
    index_body_content += "<h1>Project Index by Tag</h1>\n"
    
    # Separate the 'unsorted' tag from others
    unsorted_projects = tagged_projects.pop("unsorted", None)

    # Add all other tags first
    for tag, projects in sorted(tagged_projects.items()):
        index_body_content += f"<h2>{tag}</h2>\n<ul>\n"
        for project in sorted(projects):
            project_link = f"{project}.html"
            index_body_content += f'\t<li><a href="{project_link}">{project}</a></li>\n'
        index_body_content += "</ul>\n"
    
    # Add 'unsorted' tag last, if it exists
    if unsorted_projects:
        index_body_content += "<h2>unsorted</h2>\n<ul>\n"
        for project in sorted(unsorted_projects):
            project_link = f"{project}.html"
            index_body_content += f'\t<li><a href="{project_link}">{project}</a></li>\n'
        index_body_content += "</ul>\n"

    index_body_content += "</div>\n" # Close the wrapper div

    index_html = add_text_to_header_and_body_of_html(BLANK_HTML_FILE, index_header_content, index_body_content)

    save_html(subproject_directory, "index.html", index_html)

def main():
    # Read projects from subprojects.txt
    script_dir = get_absolute_path_of_where_this_script_exists()
    relative  = "../html/subprojects/subprojects.txt"
    abs_path_to_subproject_file = os.path.abspath(os.path.join(script_dir, relative))
    subproject_directory = os.path.dirname(abs_path_to_subproject_file)

    projects = get_projects_from_file(abs_path_to_subproject_file)
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
            tagged_projects["unsorted"].append(project)
        
        # Create HTML with dependencies
        html_content = create_html(project, md_html, dependencies)
        
        # Save HTML to a file
        save_html(subproject_directory, f"{project}.html", html_content)

    # Generate index.html based on tags
    generate_index_html(subproject_directory, tagged_projects)

if __name__ == "__main__":
    main()
