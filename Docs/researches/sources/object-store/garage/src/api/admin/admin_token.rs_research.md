# sources/object-store/garage/src/api/admin/admin_token.rs

Purpose: implements Admin API token management endpoints: list, lookup, create, update, delete, and describe the current bearer token.

Important handlers: `ListAdminTokensRequest` returns non-deleted table tokens plus configured daemon `metrics_token` and `admin_token` pseudo-records. `GetAdminTokenInfoRequest` finds exactly one token by ID or search. `CreateAdminTokenRequest` creates a new `AdminApiToken`, applies requested fields, persists it, and returns the secret once. `UpdateAdminTokenRequest` edits mutable parameters. `DeleteAdminTokenRequest` writes a delete tombstone. `GetCurrentAdminTokenInfoRequest` maps the presented bearer token to config pseudo-token or table token metadata.

Control flow and state: persistent state is in `garage.admin_token_table` as CRDT/deletable token records. `apply_token_updates` enforces mutual exclusion between explicit expiration and `never_expires`, then updates name, expiration, and scope CRDT fields. `admin_token_info_results` converts stored milliseconds to `DateTime<Utc>` and computes `expired` using `now_msec`.

Dependencies/integration: uses Garage table range/get/insert APIs, `AdminApiToken` model helpers, `ExpirationTime`, chrono timestamps, and shared admin `RequestHandler` contracts. Authentication enforcement lives in `api_server.rs`; this file manages persisted token metadata and scopes used by that enforcement.

Risks: `GetCurrentAdminTokenInfoRequest` assumes non-config tokens contain a `.` and unwraps `split_once`, relying on prior auth parsing. Granting `CreateAdminToken` or `UpdateAdminToken` scope is privilege escalation by design and warned in schema. Search must match exactly one candidate. Timestamp conversion uses `expect` for invalid stored values.

Test signals: cover config pseudo-token listing/current-info, ID vs search exclusivity, create returning secret once, expiration/never-expire conflict, scope updates, delete tombstones, expired filtering through server auth, and malformed current-token inputs.
