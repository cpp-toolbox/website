import subprocess
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("script.log"),  # Log to a file
        logging.StreamHandler()            # Log to the console
    ]
)

def list_and_filter_subprojects(organization, output_file):
    logging.info(f"Starting to process repositories for organization: {organization}")
    try:
        # Run the GitHub CLI command to list repositories in JSON format
        logging.info("Running GitHub CLI command...")
        result = subprocess.run(
            ["gh", "repo", "list", organization, "--limit", "1000", "--json", "name,description"],
            capture_output=True,
            text=True,
            check=True
        )
        logging.info("GitHub CLI command completed successfully.")

        # Parse the JSON response
        logging.info("Parsing JSON response...")
        repos = json.loads(result.stdout)

        # Filter for subprojects
        logging.info("Filtering repositories for subprojects...")
        subproject_names = [
            repo["name"] for repo in repos if "SUBPROJECT" in (repo.get("description") or "")
        ]
        logging.info(f"Found {len(subproject_names)} subprojects.")

        # Write filtered repository names to the output file
        logging.info(f"Writing subproject names to {output_file}...")
        with open(output_file, "w") as file:
            file.write("\n".join(subproject_names))
        logging.info(f"Subproject names written to {output_file} successfully.")

    except subprocess.CalledProcessError as e:
        logging.error("Error running the GitHub CLI command.")
        logging.error(e.stderr)
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON response from GitHub CLI.")
    except Exception as e:
        logging.exception("An unexpected error occurred.")

# Main script execution
if __name__ == "__main__":
    organization = "cpp-toolbox"  # Replace with your organization name
    output_file = "subprojects.txt"
    list_and_filter_subprojects(organization, output_file)
