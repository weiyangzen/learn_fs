# sources/storage-engines/tikv/components/api_version/Cargo.toml

## Purpose
This manifest defines the `api_version` component crate, which centralizes API-version-specific key/value encoding behavior for TiKV raw KV, TTL, API V2, and keyspace handling.

## Important APIs, Types, And Functions
The only local feature is `testexport`, used to expose test-only client tags. Dependencies include `bitflags`, `codec`, `engine_traits`, `kvproto`, `log_wrappers`, `match-template`, `tikv_util`, and `txn_types`; `panic_hook` is used in tests.

## Control Flow
Cargo uses the manifest to compile the crate and enable optional test exports. The crate itself is consumed by storage, backup, coprocessor, config, GC, debug, and test-storage components.

## State And Persistence Behavior
The manifest has no runtime state, but versioned encoding code compiled from this crate determines persistent key and value formats.

## Dependencies And Integration Points
Workspace dependencies ensure the encoding crate shares TiKV’s protobuf, transaction key, codec, and engine error types. `match-template` supports API-version dispatch macros.

## Risks And Edge Cases
Changing dependencies or features can affect broad storage compatibility. Since this crate defines persistent wire/storage encodings, semver-looking changes must be treated as data-format changes.

## Test Signals
The crate has extensive unit tests in `src/lib.rs`, `src/api_v2.rs`, and `src/keyspace.rs`. Build jobs with and without `testexport` are relevant.
