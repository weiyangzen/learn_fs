# sources/object-store/rustfs/crates/ecstore/src/tier/tier_handlers.rs

## Purpose

Centralizes admin-facing tier error constants.

## Important APIs and Types

Lazy `AdminError` statics include already-exists, not-found, name-not-uppercase, bucket-not-found, invalid-credentials, reserved-name, permission, and connect errors.

## Control Flow

No runtime flow beyond lazy initialization. Callers clone and sometimes mutate messages.

## State and Persistence Behavior

No persistent state; process-local static errors.

## Dependencies and Integration Points

Depends on `AdminError`, `StatusCode`, and `lazy_static`; used by tier manager and warm-backend probing/factory paths.

## Risks and Edge Cases

Permission/connect errors use HTTP 200 OK, which may be compatibility-driven but can surprise clients. Broad messages may need provider-specific appended detail.

## Test Signals

No direct tests; admin API tests should assert code/status mappings.
