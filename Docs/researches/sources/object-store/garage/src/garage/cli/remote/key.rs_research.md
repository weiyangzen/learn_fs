# sources/object-store/garage/src/garage/cli/remote/key.rs

Purpose: implements remote CLI access-key lifecycle and permissions.

Important APIs/types/functions: `Cli::cmd_key`, list/info/create/rename/update/delete/allow/deny/import/delete-expired command methods, and `print_key_info`.

Control flow: list sorts by created time and shows expiration. Commands resolve key patterns via admin API, then send create/update/delete/import requests. Create and update parse relative expiration through `parse_expires_in`; allow/deny mutate `create_bucket`; import requires `--yes` to discourage misuse.

State and persistence: mutates access-key metadata, secrets, expiration, and permissions via admin API. Secret key is only printed when included in response, otherwise redacted.

Dependencies and integration points: uses admin API request/response types, `format_table`, chrono local formatting, and shared remote helpers.

Risks: server-side search and response IDs are assumed. Delete-expired loops sequentially and can partially succeed. Importing an existing externally supplied key is security-sensitive and guarded only by `--yes`.

Test signals: no direct tests; should be covered by admin API tests and CLI smoke tests for key lifecycle.
