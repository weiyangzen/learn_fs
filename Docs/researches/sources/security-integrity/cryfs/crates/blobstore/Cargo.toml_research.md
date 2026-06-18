<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/Cargo.toml -->
# sources/security-integrity/cryfs/crates/blobstore/Cargo.toml

**Purpose**
This manifest defines the CryFS `blobstore` crate, which exposes blob storage abstractions and block-backed implementations.

**Important APIs, Types, And Functions**
The crate inherits workspace package metadata. It has a `testutils` feature that enables `cryfs-blockstore/testutils`, and depends on async/error/data libraries including `anyhow`, `async-trait`, `byte-unit`, `futures`, `binary-layout`, `cryfs-blockstore`, `cryfs-utils`, `cryfs-version`, and `log`. Dev dependencies include `mockall`, `rstest`, `tokio`, and blockstore test utilities.

**Control Flow**
Cargo builds the crate as part of the workspace and enables feature-dependent test helpers when requested.

**State And Persistence**
The manifest defines dependency/build state only. Runtime persistence is implemented by the crate’s blockstore-backed code.

**Dependencies And Integration Points**
It is tightly coupled to `cryfs-blockstore` for block IDs, block lifecycle, and remove results; to `cryfs-utils` for `AsyncDropGuard` and `Data`; and to workspace CI for feature checks.

**Risks**
The public `testutils` feature exposes tracking/test helper internals and must stay compatible with blockstore test features. Async trait bounds and workspace version coupling can cause broad compile failures when dependency APIs change.

**Test Signals**
Workspace CI runs this crate under default, no-default, and all-features modes, plus tests and target checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/Cargo.toml -->
