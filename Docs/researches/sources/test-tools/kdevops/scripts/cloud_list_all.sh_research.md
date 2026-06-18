# sources/test-tools/kdevops/scripts/cloud_list_all.sh

Purpose: lists cloud instances for the currently configured Terraform provider, with implemented Lambda Labs support and placeholders for other providers.

Important APIs/types/functions: reads `.config`, provider case statement, `scripts/lambdalabs_credentials.py get`, `curl` to Lambda Labs API, inline Python JSON parsing/formatting, uptime/cost display, and provider-specific placeholder commands.

Control flow: detects provider from `.config`, errors if none, for Lambda Labs obtains API key, fetches instances, formats API errors, prints a table of instances and estimated cost; for AWS/GCE/Azure/OCI prints suggested native CLI commands.

State/persistence behavior: read-only except network API calls.

Dependencies/integration: depends on kdevops `.config`, Lambda Labs credential helper, curl, Python JSON, and cloud provider APIs.

Risks/test signals: only Lambda Labs is implemented; API schema changes can break parsing. Test signals are correct provider detection, authenticated Lambda response, formatted instance table, and nonzero exit on missing credentials.
