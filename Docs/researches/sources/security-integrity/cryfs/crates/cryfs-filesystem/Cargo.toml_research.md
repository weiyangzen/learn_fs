<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/Cargo.toml -->
# sources/security-integrity/cryfs/crates/cryfs-filesystem/Cargo.toml

Purpose: manifest for `cryfs-filesystem`, the filesystem layer that sits over blob/block stores and `cryfs-rustfs`.

Important APIs/types/functions: package metadata uses workspace fields. Features include default `ancestor_checks_on_move` and `testutils` that enables test utilities in blobstore/rustfs dependencies.

Control flow: manifest dependencies wire async traits, atomic time, blob/block stores, rustfs, fsblobstore, utilities, versioning, futures, libc, maybe-owned, nix user support, log, and tokio sync.

State and persistence: no direct runtime persistence here, but dependencies indicate this crate integrates persisted blob/block storage with filesystem operations.

Dependencies/integration: comments note dependency graph concerns, especially direct blobstore/blockstore dependencies despite fsblobstore. Dev-dependencies enable multi-thread Tokio tests and blobstore testutils.

Risks/test signals: feature-gated ancestor checks are enabled by default, which affects move/rename safety. Manifest TODOs suggest dependency cleanup; no source behavior is visible in this work item.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/Cargo.toml -->
