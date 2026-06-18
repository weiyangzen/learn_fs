# sources/object-store/rustfs/crates/protocols/src/swift/ratelimit.rs

## Purpose
`ratelimit.rs` defines Swift account/container request rate limiting using an in-memory token bucket. Metadata values are expected in `limit/window_seconds` format.

## Important APIs, Types, And Functions
`RateLimit` stores limit and window seconds, with `parse` and `refill_rate`. Internal `TokenBucket` stores capacity, current tokens, refill rate, and last-refill time, with `try_consume`, `remaining`, and `reset_timestamp`. `RateLimiter` wraps a mutex-protected `HashMap<String, TokenBucket>` and exposes `check_rate_limit` and `get_status`. `extract_rate_limit` reads account or container metadata keys. `build_rate_limit_key` creates account or container scope keys.

## Control Flow
Callers are expected to parse metadata, build a key, and call `check_rate_limit` per request. The bucket refills based on whole elapsed seconds, consumes one token on success, and returns `SwiftError::TooManyRequests` with retry/reset data on exhaustion.

## State, Persistence, And Dependencies
Limiter state is process-local in memory and protected by a standard `Mutex`. It is not distributed across RustFS nodes, not durable across restart, and not backed by metadata or Redis. Configuration is read from metadata maps supplied by callers. Dependencies are standard time/collections/sync, tracing, and Swift error/result types.

## Integration Points
The module is exported by `mod.rs` and `errors.rs` knows how to render `TooManyRequests` with rate-limit headers. However, search within the Swift folder shows no active handler integration, so configured metadata does not currently throttle requests.

## Risks And Test Signals
The in-memory design cannot enforce cluster-wide fairness, can leak buckets for unbounded keys, and uses a blocking mutex inside request paths if integrated. `RateLimit::parse` permits `limit=0`, producing a zero refill rate and potential infinite/invalid retry calculations when consuming an empty bucket. Handler-local error conversion would drop detailed rate-limit headers if this module were called from `handler.rs`. Tests cover parsing, token consumption, remaining counts, extraction, and key construction, but not distributed behavior, cleanup, or handler responses.
