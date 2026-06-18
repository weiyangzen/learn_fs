# sources/object-store/rustfs/crates/iam/src/oidc.rs

## Purpose

`oidc.rs` implements the RustFS OpenID Connect provider manager. It supports browser authorization-code flow with PKCE, ID-token verification, RP-initiated logout URL generation, web-identity JWT verification for STS-style flows, provider discovery/JWKS refresh, environment and persisted-provider configuration loading, claim-to-policy mapping, and plugin-auth HTTP metrics.

## Important APIs, Types, and Functions

`OidcProviderConfig` is the central provider configuration, including ID, enabled flag, discovery URL, client credentials, scopes, alternate audiences, redirect behavior, claim names, role policy, display name, roles/groups/email/username claims, and `hide_from_ui`. Its manual `Debug` redacts `client_secret`.

`SourcedOidcProviderConfig` pairs a config with `Env` or `Persisted` source, and `merge_oidc_provider_configs()` gives environment configs precedence over persisted configs by provider ID. `OidcProviderValidationResult`, `OidcProviderSummary`, and `OidcClaims` are public result/DTO types.

`OidcSys` owns enabled provider configs, discovered provider metadata in an `RwLock<HashMap<String, ProviderState>>`, the `OidcStateStore`, and a custom `ReqwestHttpClient`. Key methods are `new`, `empty`, `has_providers`, `list_providers`, `list_visible_providers`, `authorize_url`, `exchange_code`, `create_logout_token`, `build_logout_url`, `map_claims_to_policies`, `verify_web_identity_token`, `state_store`, and `get_provider_config`.

Provider metadata helpers include `discover_provider`, `refresh_provider_state`, `ensure_provider_state`, `ensure_provider_state_if_stale`, `get_provider_state`, and `find_provider_by_issuer`. Config helpers parse environment variables and `ServerConfig` KVS entries. Standalone helpers normalize issuer URLs, build trailing-slash candidates, decode JWT payloads, and extract string/group claims with case-insensitive lookup.

`ReqwestHttpClient` adapts reqwest to `openidconnect::AsyncHttpClient`, chooses a no-proxy client for loopback/local OIDC URIs, and records rolling success/failure/RTT samples in `OIDC_PLUGIN_AUTHN_METRICS`.

## Control Flow

`OidcSys::new()` loads effective provider configs from global server config and environment. Disabled providers are skipped. Each enabled provider is discovered immediately; discovery failures are logged and leave that provider out of the active map.

`authorize_url()` validates provider ID, ensures metadata is not stale, creates PKCE challenge/verifier and nonce, configures a `CoreClient` from stored metadata, adds configured scopes, stores an `OidcAuthSession` keyed by OAuth state, and returns the generated authorization URL.

`exchange_code()` consumes the stored state, reconstructs the provider client, exchanges the code with the stored PKCE verifier and callback redirect URI, requires an ID token, verifies signature/issuer/audience/expiry/nonce, and retries once after refreshing provider metadata if verification fails. After verification it decodes the JWT payload to support custom claims and returns normalized claims, provider ID, consumed session, and raw ID token.

`verify_web_identity_token()` decodes the untrusted JWT payload only to find `iss`, finds a discovered provider with a normalized issuer match, refreshes stale metadata, parses the JWT as `CoreIdToken`, verifies signature/issuer/audience/expiry while skipping nonce, retries after JWKS refresh on failure, and then extracts claims using provider-specific claim names.

`create_logout_token()` stores a one-time opaque handle for a raw ID token. `build_logout_url()` consumes that handle, verifies the provider and metadata, returns `Ok(None)` when no end-session endpoint is advertised, parses the stored token as `CoreIdToken`, and builds an RP-initiated logout GET URL.

## State and Persistence Behavior

OIDC provider state is process-local. Configs are loaded from environment and persisted server config but are not written here. Discovered metadata and JWKS are cached in memory with a 24-hour staleness threshold (`OIDC_JWKS_REFRESH_INTERVAL`). Refresh failures during stale checks log warnings and keep the old metadata, while verification failures force a refresh attempt and retry.

Authorization and logout state are delegated to `OidcStateStore`, which is in-memory and single-use. Browser auth sessions store provider ID, PKCE verifier, nonce, and optional post-login redirect. Logout sessions store provider ID and ID token behind an opaque token.

Metrics state is global process-local rolling data protected by `Mutex`. Poisoned locks are recovered by taking the inner value and warning.

## Dependencies and Integration Points

The implementation is built on `openidconnect` core types for discovery, clients, tokens, verifier behavior, PKCE, nonce, state, and logout request construction. It integrates with `reqwest`, `url`, `rustfs_config` OIDC constants and server config, `rustfs_policy::policy::get_claim_case_insensitive`, `OidcStateStore`, `tokio::time::sleep`, and `tracing`.

Higher-level HTTP handlers are expected to call `authorize_url`, `exchange_code`, logout methods, and provider listing APIs. STS `AssumeRoleWithWebIdentity` style logic can use `verify_web_identity_token` and `map_claims_to_policies`.

## Risks and Edge Cases

`decode_jwt_payload()` intentionally does not validate tokens and must only be trusted after verification, except for the issuer lookup preflight. The code uses the unverified issuer to select a provider, then performs actual verification; this is appropriate but should remain explicit in future changes.

Provider discovery tries both trailing-slash variants and retries transient transport errors, but a provider whose discovery document issuer differs for other reasons will be excluded at startup. Startup discovery failure only logs; `has_providers()` may be false even though config exists.

`map_claims_to_policies()` maps group and configured claim values directly to policy names with optional prefix. This is flexible but depends on administrators maintaining policy names that match external claims and avoiding broad default `role_policy` values.

The HTTP metrics name says plugin authn but records every request through the OIDC discovery/token HTTP adapter, so interpretation should account for discovery, JWKS, and token exchange calls. `list_providers()` includes hidden providers intentionally for replication/admin use; UI callers must use `list_visible_providers()`.

## Test Signals

Tests cover string and group claim extraction, case-insensitive and ambiguous claim behavior, canonical group/role merging, JWT payload decode, issuer/config URL normalization, trailing-slash discovery candidates, mocked discovery success/failure, env/persisted config parsing, env-over-persisted precedence, hidden-provider listing semantics, secret redaction in debug output, enable-state parsing, mapping claims to policies, and loopback proxy bypass. These are strong helper/config tests, but full token exchange and real ID-token signature verification depend on integration coverage outside this file.
