# sources/object-store/rustfs/crates/iam/src/oidc_state.rs

## Purpose

`oidc_state.rs` provides a small process-local state store for OIDC browser flows. It stores PKCE verifiers and nonces between authorization redirect and callback, and stores logout ID tokens behind one-time opaque handles so browser storage does not need to retain the raw ID token.

## Important APIs, Types, and Functions

`OidcAuthSession` stores `provider_id`, `pkce_verifier`, `nonce`, and optional `redirect_after`. `OidcLogoutSession` stores `provider_id` and `id_token`.

`OidcStateStore` owns two `moka::future::Cache` instances: `cache` for auth sessions and `logout_cache` for logout sessions. It also keeps `last_capacity_log_at` as an `Arc<AtomicU64>` to rate-limit capacity warnings. `new()` configures both caches with `OIDC_STATE_CAPACITY` of 10,000 entries; auth state has a 5-minute TTL and logout state has a 1-hour TTL.

Public methods are `insert`, `take`, `contains`, `insert_logout`, `take_logout`, and `contains_logout`. `Default` delegates to `new()`. Internal helpers `now_unix_secs()` and `should_log_capacity_warning()` implement warning rate limiting.

## Control Flow

The auth flow stores state via `insert()` when `OidcSys::authorize_url()` builds an authorization URL. Callback handling calls `take()`, which removes and returns the session atomically through `moka`'s `remove`. A second use of the same OAuth state returns `None`, giving the higher-level flow replay protection.

`insert()` checks the auth cache's approximate `entry_count()` after insertion. At most once per 60 seconds, it runs pending cache tasks and logs either an approaching-capacity warning at 9,000 entries or a reached-capacity warning at 10,000 entries.

Logout follows the same single-use shape with `insert_logout()` and `take_logout()`, but it uses the separate 1-hour logout cache and does not currently emit capacity warnings.

## State and Persistence Behavior

All state is in memory. Sessions are lost across process restarts, and multi-node deployments need sticky handling or a higher-level design that tolerates callback routing to a node without the original state. No secrets are written to disk by this module.

The caches are bounded. At capacity, `moka` may evict according to its policy, so under heavy login/logout pressure some outstanding states may disappear before TTL. The capacity warning is rate-limited by `AtomicU64::compare_exchange`.

## Dependencies and Integration Points

This file integrates directly with `oidc.rs`, especially `authorize_url`, `exchange_code`, `create_logout_token`, and `build_logout_url`. It depends on `moka::future::Cache`, standard atomic/time primitives, `Arc`, and `tracing::warn`.

## Risks and Edge Cases

Because state is process-local, callback routing matters in clustered deployments. Replay protection is good because `take()` removes entries, but `contains()` is non-consuming and should not be used as an authorization decision by itself.

Only auth cache insertion emits capacity warnings; logout cache saturation is silent. `entry_count()` can be approximate and expired entries may not be fully purged until pending tasks run, so warnings should be treated as operational signals rather than exact accounting.

## Test Signals

Tests cover auth insert/contains/take, missing auth state, multiple auth entries, and logout insert/contains/take. They verify single-use behavior and field preservation, but do not test TTL expiry, capacity warning rate limiting, eviction behavior, or clustered callback behavior.
