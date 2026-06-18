# sources/security-integrity/cryfs/crates/fsblobstore/Cargo.toml

## Purpose
This manifest defines the `cryfs-fsblobstore` crate, the filesystem-backed blobstore layer used by CryFS. It declares shared workspace metadata, local CryFS crate dependencies, external dependencies, and an optional test utility feature.

## Important APIs, Types, and Functions
As a Cargo manifest, it exports no Rust APIs directly. Important package fields inherit `authors`, `edition`, `homepage`, `license`, `readme`, `repository`, `rust-version`, and `version` from the workspace. The crate name is `cryfs-fsblobstore`.

Dependencies include `anyhow`, `async-trait`, `binary-layout`, `binrw`, `byte-unit`, `derive_more`, `futures`, `lockable`, `log`, and local crates `cryfs-blockstore`, `cryfs-blobstore`, `cryfs-concurrent-store`, `cryfs-utils`, and `cryfs-version`.

## Control Flow
Cargo uses this file to resolve and compile the crate. The dependency graph wires fsblobstore to lower block/blob abstractions, concurrent store primitives, utility async-drop support, and versioning/layout crates.

## State and Persistence Behavior
The manifest does not perform persistence itself, but its dependencies indicate that the crate owns persistent blob layout and concurrent access over blockstore/blobstore backends. The `testutils` feature enables `cryfs-blobstore/testutils` for tests without making it part of default builds.

## Dependencies and Integration Points
This crate sits between higher filesystem code and lower block/blob storage crates. Local path dependencies tie it to the CryFS workspace, while `lockable`, `futures`, and `async-trait` support asynchronous/concurrent blob operations.

## Risks and Notes
Dependency version drift is controlled by workspace dependencies. Feature exposure is minimal: `default = []`, so tests needing utilities must opt into `testutils`. Any public API assumptions are in source files, not this manifest.

## Test Signals
The manifest's main test signal is build resolution. Enabling `testutils` should propagate blobstore test helpers; default builds should remain free of that feature.
