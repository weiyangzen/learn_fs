<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/cd_scripts/requirements.in -->
# sources/user-network-fs/gcsfuse/tools/cd_scripts/requirements.in

Purpose: pip-compile input for Python dependencies needed by release CD scripts on platforms where crcmod is installed through pip.

Important APIs, types, and functions: Contains the single top-level requirement `crcmod`.

Control flow: No executable flow. Tooling such as `pip-compile` or direct pip install consumes it to produce/install hashed requirements.

State and persistence behavior: No runtime state. It influences generated `requirements.txt` and pip-installed user packages.

Dependencies and integration points: Used by `e2e_test.sh` on RHEL/CentOS paths via `pip3 install --require-hashes -r tools/cd_scripts/requirements.txt --user`; `crcmod` supports gsutil CRC32C validation for composite object downloads.

Risks and test signals: The `.in` file itself has no hash pin; hash enforcement occurs in generated `requirements.txt`. Missing or stale compiled requirements would break the release script pip install.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/cd_scripts/requirements.in -->
