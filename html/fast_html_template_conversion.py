import os
from typing import Dict, Callable

def cpptbx_template_conversion(path_to_content_file: str, file_name: str, template_file: str):
    """
    First your regular html directory is copied to a different directory, then for each file in the
    new directory, this function gets called on each triple of the form:
        (path_to_content_file, file_name, template_file)

    For example, it could look like:
        (generated_html/mystuff.html, mystuff.html, my_custom_template.html)

    Notes:
    - you can configure fast-html to use different templates for different directories or files.
    - since this function is being called over all files in a new fresh copied directory so the paths
    given will be within this copied directory, and over-writing on the file path `path_to_content_file` is
    a safe operation
    """
    # open the template
    with open(template_file, "r") as f:
        template_lines = f.readlines()

    # generate a page title
    file_name = os.path.splitext(os.path.basename(file_name))[0]
    page_title = file_name.replace('_', ' ')

    # replace the title with the generated title
    if (file_name != "index.html"):
        title_line_index = next(i for i, s in enumerate(template_lines) if "<title>TITLE</title>" in s)
        template_lines[title_line_index] = template_lines[title_line_index].replace("TITLE", page_title)

    # replace the title with the generated title
    title_line_index = next(i for i, s in enumerate(template_lines) if "HEADER TITLE" in s)
    template_lines[title_line_index] = template_lines[title_line_index].replace("HEADER TITLE", page_title)

    # open the file with the actual content in it
    with open(path_to_content_file, "r") as f:
            content_string = f.read()

    # replace the body in the template with the body in the content file
    main_content_area_index = next(i for i, s in enumerate(template_lines) if "BODY" in s)
    template_lines[main_content_area_index] = template_lines[main_content_area_index].replace("BODY", content_string)

    # because we do this on a different directory we remove the temporary directory from path
    corrected_path = path_to_content_file.replace("generated_html/", "")
    github_link_filename = next(i for i, s in enumerate(template_lines) if "FILENAME" in s)
    template_lines[github_link_filename] = template_lines[main_content_area_index].replace("FILENAME", corrected_path)


    with open(path_to_content_file, "w") as f:
        contents = "".join(template_lines)
        f.write(contents)


template_file_to_conversion : Dict[str, Callable[[str, str, str], None]] = {
    "cpp_tbx_template.html": cpptbx_template_conversion
}
