# sources/object-store/garage/src/garage/cli/remote/admin_token.rs

Purpose: implements remote CLI administration-token management.

Important APIs/types/functions: `Cli::cmd_admin_token`, list/info/create/rename/update/delete/delete-expired command methods, and helper `print_token_info`.

Control flow: dispatches `AdminTokenOperation` variants to admin API requests. Create parses optional expiration and scope CSV, prints secret token once unless quiet. Update supports scope replacement plus `+scope` additions and `-scope` removals. Delete operations require `--yes` and resolve token search strings to IDs first.

State and persistence: mutates admin-token metadata through remote admin API calls. It never stores secret tokens locally; it prints newly created token secrets only once from the API response.

Dependencies and integration points: uses `garage_api_admin::api` request/response types, shared `Cli::api_request`, `parse_expires_in`, `table_list_abbr`, `format_table`, and chrono local time formatting.

Risks: token search must uniquely resolve server-side; `.unwrap()` on token IDs/created fields assumes admin API invariants. Scope CSV parsing trims entries but does not reject empty strings locally. Expiration parsing uses local current time through `parse_expires_in`.

Test signals: no local tests; API-level tests and CLI smoke tests should cover create/update/delete and scope modifications.
