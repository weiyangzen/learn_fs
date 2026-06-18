# sources/test-tools/kdevops/terraform/datacrunch/extract_api_key.py

## Purpose
This Python helper reads DataCrunch credentials from an INI file and emits JSON suitable for Terraform's external data source.

## Important APIs, Types, And Functions
`extract_credentials(creds_file)` expands the path, validates existence, parses it with `configparser`, chooses `[default]` or `DEFAULT`, extracts `client_id`, and extracts `client_secret` from `client_secret`, `datacrunch_api_key`, or `api_key`. The CLI defaults to `~/.datacrunch/credentials` and prints `{"client_id": "...", "client_secret": "..."}`.

## Control Flow
The script validates the file and required keys, writes error messages to stderr, and exits 1 on any failure. On success it prints JSON to stdout.

## State And Persistence
It reads credential files but writes no state. Secret values are transiently held in memory and printed to stdout for Terraform consumption.

## Dependencies And Integration Points
It depends on Python standard `configparser`, `json`, `sys`, and `pathlib`. It integrates with Terraform `external` data sources and DataCrunch provider authentication.

## Risks And Test Signals
Printing secrets to stdout is required by Terraform external data flow but means logs must not capture it. `ConfigParser` default-section handling is subtle: `DEFAULT` is always present but may not represent an explicit section. Errors are broad and exit immediately, which is fine for CLI use but harder for library reuse. Tests should cover missing file, missing section, legacy key names, whitespace trimming, explicit path argument, and JSON shape.
