# sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/file.rs

Purpose: Implements in-memory file inode and open-file behavior.

Important APIs/types/functions: private `FileInode` stores metadata plus `Vec<u8>` data and maintains `metadata.num_bytes == data.len()`. `InMemoryFileRef` creates/clones/opens files and handles metadata changes. `InMemoryOpenFileRef` implements getattr, setattr, read, write, flush, and fsync.

Control flow: opening captures `OpenInFlags`. Reads reject write-only handles; writes and size-changing setattr reject read-only handles. Writes extend the vector with zeros when offset+data exceeds current length, then copies bytes into place.

State and persistence behavior: data and metadata live in memory under `Arc<Mutex<FileInode>>`; flush and fsync are no-ops.

Dependencies and integration points: used by in-memory dirs and nodes; exercises `object_based_api::File` and `OpenFile` contracts for backend tests/examples.

Risks: read computes `data.len() - offset` and can underflow/panic if offset exceeds file length. Several integer conversions unwrap. Timestamp maintenance is incomplete.

Test signals: tests should include read beyond EOF, sparse writes, read/write permission errors, truncate through setattr, and metadata size invariant checks.
