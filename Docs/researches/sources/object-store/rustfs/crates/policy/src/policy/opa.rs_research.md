# sources/object-store/rustfs/crates/policy/src/policy/opa.rs

## Purpose

Implements optional Open Policy Agent authorization integration. It discovers OPA plugin configuration from environment variables, validates connectivity, builds an HTTP client, converts RustFS policy request arguments to an OPA input document, and interprets supported OPA response shapes.

## Important APIs, Types, and Functions

- `Args { url, auth_token }` holds plugin configuration. `Args::enable()` returns true when a URL is configured.
- `check()` validates environment configuration. It requires `ENV_POLICY_PLUGIN_OPA_URL`, permits `ENV_POLICY_PLUGIN_AUTH_TOKEN`, and rejects unknown variables under the policy plugin prefix.
- `validate(config)` posts to the configured URL and requires HTTP 200 to consider OPA reachable.
- `lookup_config()` reads env vars, returns disabled default when the URL is absent, otherwise checks and validates the config.
- `AuthZPlugin::new(config)` builds a tuned `reqwest::Client` with short timeouts, keepalive, pooling, HTTP/2 keepalive, and TCP no-delay.
- `AuthZPlugin::is_allowed(args)` sends the OPA JSON payload, adds a bearer token when present, and fail-closes on transport, status, or JSON parse errors.
- `build_opa_input(args)` maps policy arguments into `input.identity`, `input.resource`, `input.action`, and `input.context`.
- `OpaResponseEnum` accepts either `{ "result": bool }` or `{ "result": { "allow": bool } }`.

## Control Flow

Startup config flow calls `lookup_config`: no URL means disabled; otherwise the environment is screened for unknown plugin settings and the endpoint is probed. Runtime authorization constructs payload from `PArgs`, posts JSON to `args.url`, optionally adds `Authorization: Bearer <token>`, checks for a successful HTTP status, then deserializes a supported OPA result form. Any failure logs an error and returns false.

## State and Persistence

The plugin retains only a `reqwest::Client` and cloned config. There is no persistence. Runtime payloads include the current UTC timestamp using `chrono::Utc::now().to_rfc3339()`.

## Dependencies and Integration Points

Depends on `rustfs_config::opa` constants for environment names, `reqwest` for HTTP, `serde_json` for payloads, `tracing` for logs, and `crate::policy::Args` for RustFS authorization context. It integrates as an external authorizer alongside or in front of local policy evaluation depending on caller wiring.

## Risks and Edge Cases

- Connectivity validation sends an empty POST to the policy URL; OPA policies that reject empty input may make startup fail.
- HTTP client construction uses `.unwrap()`, so invalid TLS/client configuration would panic, though the builder options are static.
- Authorization is fail-closed, which is appropriate for security but makes OPA availability a hard dependency once enabled.
- Only two response shapes are accepted; richer OPA documents must be adapted in policy or code.
- Environment screening rejects any unknown variable under the plugin prefix, which can catch typos but may surprise deployments with extra metadata env vars.

## Test Signals

Inline tests cover valid env config, missing URL, invalid env vars, disabled lookup behavior, and `Args::enable`. There are no HTTP mock tests for `validate` or `is_allowed`, so response parsing and fail-closed behavior are visible in code but not directly exercised here.
