# Description:
A simple tool to manage addons for Guild Wars 2.

# Building:
Run `pyinstaller packaging.spec`.

# Application:
See `/dist/gw2-addon-manager.exe`

# Configuration:
The following is a breakdown of typical configuration files and their subsequent keys:
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

# Moving the Application:
If you intend to relocate the application do one of the following:
- Ensure you keep `gw2-addon-manager.exe`, `configs`, and `logs` together in the same parent folder.
