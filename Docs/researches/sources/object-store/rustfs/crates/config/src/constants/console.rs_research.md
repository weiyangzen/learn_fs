<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/console.rs -->
# sources/object-store/rustfs/crates/config/src/constants/console.rs

## Purpose
Defines public environment names and defaults for S3 endpoint CORS, management console CORS, console enable/address settings, console rate limiting, console auth timeout, and update checks.

## Important APIs, types, and functions
`ENV_CORS_ALLOWED_ORIGINS` and `ENV_CONSOLE_CORS_ALLOWED_ORIGINS` distinguish S3 endpoint and console CORS policy. `DEFAULT_*_CORS_ALLOWED_ORIGINS` are intentionally empty. Console rate-limit knobs are `ENV_CONSOLE_RATE_LIMIT_ENABLE`, `ENV_CONSOLE_RATE_LIMIT_RPM`, and defaults `false`/`100`. `ENV_CONSOLE_AUTH_TIMEOUT` defaults to `3600` seconds, and `ENV_UPDATE_CHECK` defaults to `true`.

## Control flow
There is no runtime control flow beyond unit tests asserting the restrictive empty CORS defaults and stable env names.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Consumed by server/config loaders and console HTTP setup. It integrates with browser CORS behavior, rate-limit middleware, console session/auth handling, and update-check scheduling.

## Risks and edge cases
The security-sensitive behavior is that empty CORS means no generic cross-origin access; changing it to `*` would reopen broad browser access. Rate limiting defaults to off, so deployments expecting protection must opt in. Timeout values are only enforced if downstream parsing validates range comments.

## Test signals
Unit tests currently pin endpoint and console CORS env names/defaults. Broader signals should include browser CORS responses, console rate-limit activation, auth-session expiry, and update-check disablement.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/console.rs -->
