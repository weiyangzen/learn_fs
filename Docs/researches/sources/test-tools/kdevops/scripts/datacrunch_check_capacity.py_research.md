<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_check_capacity.py -->
# sources/test-tools/kdevops/scripts/datacrunch_check_capacity.py

Purpose: CLI capacity checker for DataCrunch GPU instance availability. It supports spot availability via `/instance-availability`, on-demand deployability via `/instance-types` plus `/locations`, JSON output for automation, and `--pick-first` for Ansible/Terraform selection flows.

Important APIs and functions: `load_credentials()` reads an INI credentials file, accepting `client_secret`, `datacrunch_api_key`, or `api_key`; `get_oauth_token()` posts to `/oauth2/token` with `requests`; `check_availability()` returns a list of location records for a specific instance or capacity maps; `main()` parses `--instance-type`, `--location`, `--json`, `--pick-first`, `--credentials`, and `--on-demand`.

Control flow: credentials are loaded, an OAuth token is acquired, capacity is queried, then output mode decides whether to print first location, JSON, or human-readable availability. The spot path filters `availabilities`; the on-demand path treats listed instance types as deployable in every returned location.

State and persistence: reads credentials only; no writes. Exit codes carry availability: no results for a requested instance exits nonzero, and API/credential failures exit immediately.

Dependencies and integration: depends on third-party `requests`. `datacrunch_select_tier.py` invokes it, and Terraform bringup playbooks call it for location and capacity checks.

Risks: on-demand location mapping is approximate and may overstate deployability. The help text still mentions setting only a client secret in one error path, while code requires both client ID and secret. It exits within helper functions, which makes library-style reuse hard. Test signals include mocking `requests`, verifying JSON shapes, `--pick-first` behavior, credentials variants, and nonzero exit when capacity is absent.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_check_capacity.py -->
