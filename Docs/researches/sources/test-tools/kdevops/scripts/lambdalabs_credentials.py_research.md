# sources/test-tools/kdevops/scripts/lambdalabs_credentials.py

## Purpose
`lambdalabs_credentials.py` manages Lambda Labs API keys stored in INI-style credentials files, with a CLI for get/set/check/test/path operations.

## Important APIs, Types, And Functions
Exports are `get_credentials_file_path()`, `read_credentials_file(path=None, profile="default")`, `get_api_key(profile="default")`, `create_credentials_file(api_key, path=None, profile="default")`, and `main()`. The default path is `~/.lambdalabs/credentials`.

## Control Flow
Credential reading checks the default file, then a custom `LAMBDALABS_CREDENTIALS_FILE`, and looks for `lambdalabs_api_key` or `api_key` under the requested profile or `DEFAULT`. Creation ensures the parent directory, updates the profile, writes the file, and chmods it `0600`. CLI `test` calls the Lambda Labs `/instances` endpoint with the key and reports validity.

## State And Persistence
Persistent state is the credentials file on disk. `set` writes or updates it with restrictive permissions. Other commands read and print status or secret values.

## Dependencies And Integration Points
Depends on `configparser`, `Path`, `os`, and optional urllib/json in `test`. Imported by Lambda Labs API and SSH key modules. External scripts expect `get_api_key()` to be the central credential source.

## Risks And Edge Cases
Despite callers' comments, this module does not read `LAMBDALABS_API_KEY` directly. Parse errors are silently ignored. `get` prints the raw API key to stdout. `test` distinguishes HTTP 403 but other failures are generic. Existing file comments/order may be rewritten by `configparser`.

## Test Signals
Test missing file, profile-specific key, DEFAULT key, custom credentials path, file creation permissions, parse failure, CLI get/check/path/set, and mocked API test success/403/other error.
