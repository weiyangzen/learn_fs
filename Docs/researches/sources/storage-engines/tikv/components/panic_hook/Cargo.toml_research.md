# sources/storage-engines/tikv/components/panic_hook/Cargo.toml

## Purpose
This manifest defines the private `panic_hook` test utility crate.

## Important APIs, Types, and Functions
It sets package metadata only: name, version, edition, unpublished status, and license. There are no runtime dependencies.

## Control Flow
No manifest control flow.

## State and Persistence Behavior
No state in the manifest.

## Dependencies and Integration Points
The crate is used as a dev dependency by low-level crates that need to assert panics without printing stack traces.

## Risks
Because production TiKV uses fatal panics, this crate should remain test-only. Adding it as a production dependency would conflict with its own documentation.

## Test Signals
The manifest has no tests.
