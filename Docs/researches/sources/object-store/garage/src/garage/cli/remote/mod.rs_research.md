# sources/object-store/garage/src/garage/cli/remote/mod.rs

Purpose: remote CLI module aggregator and shared admin RPC helper implementation.

Important APIs/types/functions: modules `admin_token`, `bucket`, `cluster`, `key`, `layout`, `block`, `node`, `worker`; struct `Cli`; methods `handle`, `api_request`, `local_api_request`, `cmd_json_api`; helpers `table_list_abbr` and `parse_expires_in`.

Control flow: `handle` dispatches high-level `Command` variants to domain modules. `api_request` wraps typed admin API requests in proxy RPC, maps typed responses, and turns admin API errors into CLI errors. `local_api_request` wraps a typed request in `MultiRequest` scoped to `rpc_host`, then requires exactly one successful response. `cmd_json_api` accepts JSON from argument or stdin, sends raw endpoint payload, and pretty-prints the matching response field.

State and persistence: no direct persistence; every mutation occurs through remote admin API/RPC. Holds RPC endpoint and target node ID.

Dependencies and integration points: central integration with `garage_rpc`, `garage_api_admin::api`, `AdminRpc` proxy server, `RequestHandler`, CLI structs, chrono/date parsing, and parse-duration.

Risks: typed response conversion failures are surfaced as unexpected responses. `local_api_request` ignores all but the first error and requires a single success, which is correct for a single target but sensitive to `MultiResponse` shape. Raw JSON API bypasses typed CLI validation.

Test signals: no direct tests; any remote command exercises these helpers. High-value tests include API error formatting, typed conversion mismatch, stdin JSON path, and multi-response error handling.
