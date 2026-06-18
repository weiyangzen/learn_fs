# sources/object-store/rustfs/crates/protocols/tests/swift_listing_symlink_tests.rs

## Purpose

This Swift-feature-gated Rust test module exercises the symlink helpers in `rustfs_protocols::swift::symlink`. The module-level comment also names container-listing coverage, but the actual source file is focused on symlink metadata detection, target parsing, empty/invalid target handling, special characters, loop-detection data structure expectations, maximum traversal depth, and the boundary between symlink targets and request query parameters.

## Important APIs, types, and functions

- Imports `rustfs_protocols::swift::symlink::*` and uses `HashMap<String, String>` as object metadata.
- `is_symlink(&HashMap<String, String>)` is expected to return true solely when metadata contains `x-object-symlink-target`.
- `get_symlink_target(&HashMap<String, String>)` returns `SwiftResult<Option<SymlinkTarget>>`, producing `None` when the header is absent and an error when the header exists but cannot be parsed.
- `SymlinkTarget::parse(&str)` accepts `container/object`, nested object paths after the first slash, and same-container object names without slash.
- `SymlinkTarget` exposes `container: Option<String>` and `object: String`.
- `validate_symlink_depth(depth: u8)` enforces a maximum depth of five hops, with depths `0..5` accepted and depth `5` rejected.

## Control flow

Each test constructs metadata or target strings, invokes a pure helper, and asserts either the parsed structure or the expected failure. Parsing is validated in two layers: direct `SymlinkTarget::parse` tests and metadata-driven `get_symlink_target` tests. Loop detection is represented by inserting link names into a `HashSet` and asserting that revisiting a prior link would be detectable. The depth test uses a local `MAX_SYMLINK_DEPTH` constant equal to the implementation limit and checks the boundary exactly.

## State and persistence behavior

There is no durable state. All state is local test data: metadata maps, parsed target values, and an in-memory `HashSet` representing visited symlink paths. The tests imply that production symlink traversal should maintain per-request visited state and depth counters rather than storing symlink resolution state in object metadata.

## Dependencies and integration points

The file depends on the `swift` Cargo feature and the Swift symlink module. It indirectly validates request-handler behavior because handlers write and read `x-object-symlink-target` metadata, while GET/HEAD code can later use `get_symlink_target`, `validate_symlink_depth`, and visited-path tracking to resolve links safely. The tests are also tied to Swift API header naming: the accepted header is `x-object-symlink-target`, not the shorter response header spelling.

## Risks and edge cases

- The module comment promises container listing tests, but no listing code appears in this file. That mismatch can mislead maintainers looking for prefix, delimiter, marker, or limit coverage.
- `is_symlink` is intentionally header-presence based. A metadata map with an empty or malformed target is still classified as a symlink and only fails when parsed.
- Query parameters are not stripped or parsed here; callers must ensure they pass only the target header value.
- The loop-detection test validates a generic `HashSet` pattern, not the implementation's `SymlinkPath` or `check_circular_reference` function.
- The tests use lower-case metadata keys, so they do not prove header normalization for mixed-case inputs.

## Test signals

This file provides focused unit test signals for valid and invalid target parsing, same-container targets, special-character preservation, empty target failure, metadata format expectations, and maximum symlink depth. Missing signals include real handler GET/HEAD symlink following, circular-reference errors through the production API, authorization checks, and container-listing behavior named in the header comment.
