# sources/object-store/rustfs/crates/filemeta/src/lib.rs

## Purpose

This is the crate root for `rustfs-filemeta`. It defines the module structure and re-export surface for file metadata, file info, inline data, metacache, replication, errors, and test fixtures.

## Important APIs, Types, and Functions

The file declares private modules `error`, `fileinfo`, `filemeta`, `filemeta_inline`, `metacache`, and `replication`; `headers` is present but commented out. It exposes `test_data` publicly as a module and then publicly re-exports all items from `error`, `fileinfo`, `filemeta`, `filemeta_inline`, `metacache`, and `replication`.

## Control Flow

There is no runtime control flow. Compilation wires the crate modules and glob re-exports so downstream crates can import public types from the crate root rather than deep module paths.

## State and Persistence Behavior

No state is stored here. Persistence behavior is delegated to the re-exported modules, especially `filemeta`, `filemeta_inline`, `metacache`, and `replication`.

## Dependencies and Integration Points

This root controls integration for all crate consumers. The broad glob re-exports mean changes to any exported public type in the child modules immediately affect the crate-level API. `pub mod test_data` also exposes fixture builders to downstream test code.

## Risks and Edge Cases

- Glob re-exports can create API ambiguity if child modules introduce same-named public items.
- Because `test_data` is public in all builds, fixture helpers and fixture include paths become part of the visible crate surface unless gated elsewhere.
- The commented `headers` module hints at either removed or pending API; consumers cannot access it through this crate root.

## Test Signals

There are no tests in this file. Its behavior is implicitly covered by any crate compilation or downstream imports using the root exports.
