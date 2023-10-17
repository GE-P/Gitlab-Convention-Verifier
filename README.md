![Alt text](docs/image.png)
## Description

This Python script is designed to verify and potentially correct naming and structure conventions for GitLab projects and groups. It utilizes the GitLab API and offers an option for auto-correction if enabled.

## Prerequisites

Before using this script, ensure you have the following prerequisites:

- Python 3.x installed
- Required Python modules (install using pip):
    - gitlab
    - urllib3
    - colorama
    - inflection
    - pymsteams
    - python-dotenv

-Or using the requirements file: 

    pip install -r requirements.txt


## Setup

- Clone the repository to your local machine.

- Create a .env file in the same directory as the script with the following variables:
    - gitlab_url: Your GitLab server URL.
    - private_token: Your GitLab private token for authentication.
    - teams_url: Microsoft Teams webhook URL for reporting.

## Usage

Run the script using Python 3.x:

    python gitlab_convention_verifyer.py

- The script will connect to your GitLab server and perform the following checks on projects:

    - Naming convention for project names (snake_case).
    - Naming convention for group names (CamelCase).
    - Structure of branches within each project.

- Optionally, you can enable auto-correction by changing the auto_correction variable in the script to 1.

## Reporting

If a project does not meet the conventions or has structural issues, the script will report the project and the users who need to be informed. It will send a message to Microsoft Teams using the provided webhook URL.

## Notes

- The script uses the GitLab API and may require appropriate permissions to access your GitLab server.

- Make sure to install the required Python modules using pip before running the script.