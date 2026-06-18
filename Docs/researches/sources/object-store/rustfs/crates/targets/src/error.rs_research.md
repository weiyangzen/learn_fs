# sources/object-store/rustfs/crates/targets/src/error.rs

## Purpose
Defines shared error enums for target storage and delivery/runtime operations.

## Important APIs, types, and functions
- `StoreError` covers queue-store I/O, serialization, deserialization, compression, limits, missing entries, and internal invalid entries.
- `TargetError` covers storage, network, request, timeout, authentication, configuration, encoding, serialization, connection state, initialization, invalid ARN, disabled targets, dropped queued payloads, parse failures, save-config failures, and uninitialized server state.
- `impl From<url::ParseError> for TargetError` maps URL parse failures to configuration errors.

## Control flow
The file has no branching behavior beyond the URL parse error conversion. Error display strings are supplied through `thiserror`.

## State and persistence behavior
No state is stored. These error variants are used to classify state transitions elsewhere, especially replay behavior where `Timeout` and `NotConnected` are retryable, `Dropped` is terminal, and other errors are permanent.

## Dependencies and integration points
It depends on `std::io`, `thiserror`, and `url`. The enums are re-exported by `lib.rs` and used across target implementations, queue stores, config validation, connectivity checks, runtime replay, and plugin registry code.

## Risks and edge cases
Many variants carry strings instead of structured fields, so callers often inspect the variant but cannot reliably parse causes. Adding variants can require replay and admin mapping updates. `TargetError::Configuration` is used broadly for both parse failures and policy failures.

## Test signals
No direct tests are present. Variant behavior is exercised throughout config, connectivity, runtime, and target module tests via pattern matching and display-string assertions.
