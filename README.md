# Description:
A simple tool to manage addons for Guild Wars 2.

# Application:
Please download the latest release [here](https://github.com/Jared-Hinze/gw2-addon-manager/releases/latest).

# Configuration:
The `configs/` folder holds the following user customizable configuration files.
## settings.yaml:
This file will largely be for individual customization of the application's behaviors
- **install_path**:
  - Description: The folder where Gw2-64.exe is found.
  - Value: Any valid folder path.
- **close_on_success**:
  - Description: Close the application automatically if all downloads succeed.
  - Values (case insensitive):  `T | F | Y | N | True | False | Yes | No | On | Off`

## addons.yaml
This file is where users can add/remove typical third-party installations.
This will change which DLL's are available to control in the gw2-addon-manager application window.
There are two kinds of DLL tags and each resource MUST be tagged accordingly:
- **!RawAddon**: These are direct paths to online DLL resources.
  - Fields:
    - **dll**: The name of the DLL.
    - **url**: The URL to the resource. Generally get this via "right-click > Copy Link" where you'd otherwise download.
    - **dst** (optional): The folder the DLL saves in. Omit this if the DLL belongs in the root directory.
- **!GitAddon**: These are addons that specifically come from GitHub.
  - Fields:
    - **dll**: The name of the DLL.
    - **owner**: The owner of the repository as seen in the URL e.g. github.com/\<owner\>
    - **repo**: The target repository the resource comes from e.g. github.com/\<owner\>/\<repo\>
    - **dst** (optional): The folder the DLL saves in. Omit this if the DLL belongs in the root directory.

## logging.yaml
This file is largely to configure Python's logging.py logger.

Please refer to https://docs.python.org/3/library/logging.config.html#logging-config-dictschema.

# Portfolio Highlights:
This project demonstrates a variety of important industry standards and techniques along with innovative approaches.<br />
Note: some of the approaches taken were solely for the purpose of demonstrating knowledge/skills.
## VCS:
- Git/GitHub
- Pre-commit (coming soon)
- Semantic Versioning
- Dependency Groups
- Lock Files
- Licensing
- Code Signing
## CI/CD:
- Automated Workflows
  - Version Bumping
  - Status Checks
    - Unit Tests (coming soon)
    - Verify PR Builds Complete
  - Tagging
  - Releasing
- Reusable Workflows
- Bot Assistance
## Python:
- Packaging
- MVC Design Pattern
- Cross Platform Design
- Threading
- Calling RESTful APIs
- Advanced YAML Parsing
- Logging
- Enumeration
