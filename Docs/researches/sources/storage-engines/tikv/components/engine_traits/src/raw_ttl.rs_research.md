# sources/storage-engines/tikv/components/engine_traits/src/raw_ttl.rs

Purpose: Provides RawKV TTL timestamp helpers.

Important APIs and control flow: `ttl_current_ts` returns current Unix seconds and has a failpoint override. `ttl_to_expire_ts` maps zero TTL to `None` and nonzero TTL to `current + ttl` with saturating addition.

State, persistence, and dependencies: Helpers are stateless, but generated expiration timestamps are persisted inside encoded raw values by callers. Dependencies include failpoints and TiKV time utilities.

Integration points, risks, and test signals: Used by RawKV write paths and TTL property collection. Risks include clock skew, saturating overflow hiding very large TTLs, failpoint-only test behavior, and semantic differences between absent TTL and expire-ts zero. Tests should use failpoints for deterministic timestamps.
