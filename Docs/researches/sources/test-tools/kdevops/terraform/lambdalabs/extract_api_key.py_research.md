# sources/test-tools/kdevops/terraform/lambdalabs/extract_api_key.py

Purpose: Terraform external-data helper that extracts a Lambda Labs API key from a credentials file and prints JSON as `{"api_key": "..."}`.

The main API is `extract_api_key(creds_file="~/.lambdalabs/credentials")`. It expands the path, requires the file to exist, parses it with `configparser.ConfigParser`, and looks for `lambdalabs_api_key` in either a `default` section or the parser `DEFAULT` section. On errors or missing keys it writes to stderr and exits with status 1.

Control flow is simple: choose CLI path or default path, call extractor, print JSON. State read is user-local credentials; output is stdout JSON for Terraform. Dependencies are `configparser`, `json`, `sys`, and `pathlib`.

Risks include the credential format mismatch with `SET_API_KEY.sh`, broad exception handling that may hide parse details, and no permission check despite the shell guidance recommending `600`. Test signals should include missing file, malformed INI, `default` section, `DEFAULT` values, custom path argument, JSON output shape, and absence of secret leakage to stderr.
