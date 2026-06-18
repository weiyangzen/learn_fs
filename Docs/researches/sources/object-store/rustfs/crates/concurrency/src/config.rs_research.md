# sources/object-store/rustfs/crates/concurrency/src/config.rs

## Purpose
Defines the top-level configuration object and validation rules for the concurrency facade.

## Important APIs, types, and functions
`ConcurrencyFeatures` carries booleans for timeout, lock, deadlock, backpressure, and scheduler with `all`, `none`, and `any_enabled`. `LockManagerPolicy` stores lock enablement and acquisition timeout. `ConcurrencyConfig` aggregates feature flags and each module policy. `from_env` reads selected environment variables. `validate` returns `ConfigError` variants for timeout, backpressure, and scheduler errors.

## Control flow
`Default` feature flags use `cfg!(feature = "...")`; policy defaults come from their module types. `from_env` overlays timeout defaults/max, backpressure buffer size, and scheduler base buffer size. `validate` enforces timeout ordering, high watermark greater than low and at most 100, and base buffer not exceeding max buffer.

## State and persistence behavior
The file defines cloneable in-memory config. Environment variables are read at construction time; there is no dynamic reload or persistence.

## Dependencies and integration points
Pulls policy types from `timeout`, `deadlock`, `backpressure`, and `scheduler`. `ConcurrencyManager::new` calls `validate` and panics on errors, making this the primary safety gate for facade construction.

## Risks and edge cases
Only four env vars are supported, leaving many policy fields unconfigurable from environment. `lock_policy.enabled` and `features.lock` can diverge. `validate` does not check low watermark bounds, zero buffer sizes, deadlock interval thresholds, or scheduler priority threshold ordering.

## Test signals
Tests cover default validation success, invalid default/max timeout, invalid min/max timeout, and feature helper behavior.
