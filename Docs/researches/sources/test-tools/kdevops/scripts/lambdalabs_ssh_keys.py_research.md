# sources/test-tools/kdevops/scripts/lambdalabs_ssh_keys.py

## Purpose
`lambdalabs_ssh_keys.py` manages Lambda Labs SSH keys through the cloud API: list, add, delete, check existence, read public key files, and validate that a named key is available for kdevops provisioning.

## Important APIs, Types, And Functions
Exports include `get_api_key()`, `make_api_request()`, `list_ssh_keys()`, `add_ssh_key()`, `delete_ssh_key()`, `read_public_key_file()`, `check_ssh_key_exists()`, `validate_ssh_setup()`, and `main()`. Constant `LAMBDALABS_API_BASE` points at the v1 API.

## Control Flow
`make_api_request()` builds authenticated requests, optionally encodes JSON for write methods, and returns parsed JSON or `None`. Listing expects `{"data": [...]}` but accepts list responses. Adding tries `{"name","public_key"}` then an alternate `{"name","key"}` payload. Deleting resolves names to IDs by listing keys before issuing `DELETE /ssh-keys/<id>`. Validation lists keys, handles unsupported API/no keys/missing expected key cases, and returns a success flag with human guidance.

## State And Persistence
No local files are written. The script mutates remote Lambda Labs SSH key state on `add` and `delete`. It reads local public key files for `add`.

## Dependencies And Integration Points
Depends on `lambdalabs_credentials.py`, `urllib.request`, `urllib.error`, `json`, `os`, `sys`, and typing. It supports Terraform identity workflows that require SSH keys to exist in Lambda Labs.

## Risks And Edge Cases
Remote API schema support is uncertain, reflected by fallback payloads and manual-console guidance. HTTP errors print details but return only `None`. `delete_ssh_key()` only treats 32-character hex strings as IDs. `except:` around error-body reading is broad. Adding duplicate keys or names depends on remote API behavior.

## Test Signals
Mock API responses for list data/list/raw/none, add first-format success, alternate-format success, delete by ID/name/not-found, public key missing/read error, validate unsupported/no keys/missing/found, no credentials, and CLI exit codes.
