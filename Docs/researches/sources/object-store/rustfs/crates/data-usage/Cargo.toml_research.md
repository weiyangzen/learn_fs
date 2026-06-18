# sources/object-store/rustfs/crates/data-usage/Cargo.toml

## Purpose
This manifest defines the `rustfs-data-usage` crate, which provides shared data-usage models and cache algorithms for RustFS storage usage reporting.

## Important APIs, Types, and Functions
The manifest identifies the crate as a library with doctests disabled. Its package metadata is workspace-driven for version, edition, license, repository, rust version, and homepage. The description, keywords, and categories position it as a data-structure and filesystem-oriented crate.

## Control Flow
There is no runtime control flow in the manifest. It controls compilation by selecting workspace dependencies and applying workspace lint settings.

## State and Persistence
Persistence support is implied by dependencies on `serde` and `rmp-serde`, which are used by `data_usage.rs` for serializing `DataUsageCache` and usage models. No build script or generated state is declared.

## Dependencies and Integration Points
The crate depends on `serde`, `path-clean`, `rmp-serde`, `async-trait`, and `rustfs-filemeta`. These map directly to path normalization, MessagePack cache serialization, async storage traits, and object metadata conversion in the source.

## Risks and Edge Cases
Because versions and dependency settings are inherited from the workspace, compatibility depends on workspace-level changes. Disabling doctests is appropriate for a model crate without examples, but it means documentation snippets would not be validated if added later.

## Test Signals
The manifest has no direct tests. Test coverage comes from `src/data_usage.rs` unit tests and e2e tests that deserialize `rustfs_data_usage::DataUsageInfo` from admin APIs.
