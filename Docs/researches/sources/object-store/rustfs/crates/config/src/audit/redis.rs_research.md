# sources/object-store/rustfs/crates/config/src/audit/redis.rs

## Purpose
Declares Redis audit target environment variables and configuration keys, including retry, timeout, pipeline, queue, and TLS options.

## Important APIs, types, and functions
Exports 20 `ENV_AUDIT_REDIS_*` constants and `ENV_AUDIT_REDIS_KEYS`. `AUDIT_REDIS_KEYS` covers enablement, URL, channel, username/password, keepalive, queue dir/limit, retry attempts, min/max retry delays, connection/response timeouts, pipeline buffer size, TLS policy/material, insecure TLS, and comments.

## Control flow
No runtime flow; consumers iterate static key arrays.

## State and persistence behavior
Static string metadata only. The default Redis channel is declared in `audit/mod.rs`, not here.

## Dependencies and integration points
References shared Redis config key constants and is re-exported through `audit/mod.rs`. Redis audit sink code consumes these for connection setup and buffering behavior.

## Risks and edge cases
Many numeric/time values require downstream parsing and bounds checks. TLS allow-insecure is security-sensitive. Array length and config/env parity are manually maintained. The default channel being outside this file can surprise maintainers.

## Test signals
No local tests; integration coverage should validate retry/timeout/env parsing and default channel behavior.
