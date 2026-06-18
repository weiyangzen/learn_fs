<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_credentials.py -->
# sources/test-tools/kdevops/scripts/datacrunch_credentials.py

Purpose: manages DataCrunch OAuth2 credentials in `~/.datacrunch/credentials`, with profile support and a command-line utility for setting, checking, retrieving, and testing credentials.

Important APIs and functions: `get_credentials_file_path()` returns the default credentials path; `read_credentials_file()` parses an INI profile and DEFAULT fallbacks; `get_credentials()` checks the default path first, then `DATACRUNCH_CREDENTIALS_FILE`; `get_api_key()` returns the client secret for backward compatibility; `create_credentials_file()` creates or updates a profile and chmods the file to `0600`; `main()` implements `get`, `set`, `check`, `test`, and `path`.

Control flow: library callers read credentials without side effects. The `set` command prompts for client ID and hidden client secret, writes the INI file, and reports test instructions. The `test` command obtains an OAuth token and queries `/instances`.

State and persistence: writes `~/.datacrunch/credentials` or reads an environment-specified file. Secrets are stored in plaintext INI form but with restricted permissions when this script writes them.

Dependencies and integration: standard library only. It is imported by `datacrunch_api.py` and indirectly by DataCrunch Kconfig and SSH-key helpers.

Risks: parse errors are silently ignored in `read_credentials_file()`, which can obscure configuration problems. The `check` command masks all but the final four characters but assumes secret length is at least four. Usage strings still show older single-argument API key examples in a few places. Test signals include temp HOME tests for profile writes, env-file fallback, chmod checks, missing/malformed INI behavior, and mocked OAuth tests.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_credentials.py -->
