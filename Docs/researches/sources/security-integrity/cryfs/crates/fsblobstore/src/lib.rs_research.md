# sources/security-integrity/cryfs/crates/fsblobstore/src/lib.rs

Purpose: Crate root for CryFS fsblobstore.

Important APIs/types/functions: declares `concurrentfsblobstore`, `fsblobstore`, and `utils`; re-exports `ConcurrentFsBlob`, `ConcurrentFsBlobStore`, `LoadedBlobGuard`, `RequestRemovalResult`, `BlobType`, directory/file/symlink blob types, errors, `FlushBehavior`, and fs uid/gid/mode types.

Control flow: no runtime control flow. It defines the public API surface for typed blob storage.

State and persistence behavior: no state here. Exported modules implement the fsblob binary format and concurrent cache.

Dependencies and integration points: downstream CryFS filesystem layers import this crate instead of reaching into private module trees.

Risks: broad re-exports make internal error and guard types part of the public contract. Future refactors need compatibility care.

Test signals: public API compile tests and downstream crate builds are the primary signal for this file.
