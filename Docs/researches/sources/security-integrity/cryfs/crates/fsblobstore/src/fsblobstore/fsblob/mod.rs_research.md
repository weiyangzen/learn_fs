# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/mod.rs

Purpose: Typed blob enum and facade for file, directory, and symlink blobs.

Important APIs/types/functions: re-exports typed blobs, directory entry types, and errors. `FsBlob` variants hold async-drop guards for `FileBlob`, `DirBlob`, and `SymlinkBlob`. APIs include `parse`, `blob_id`, type-specific `as_*` accessors, `lstat_size`, `all_blocks`, `flush`, test-only `into_raw`, and async-drop dispatch.

Control flow: parsing first creates a `BaseBlob`, then switches on the header `BlobType`. If blob type decoding fails, it async-drops the base blob before returning the error. Callers must request the correct variant through `as_file`, `as_dir`, or `as_symlink`.

State and persistence behavior: `FsBlob` is an in-memory typed owner. Persistence is delegated to the contained typed blob. Async drop flushes directory dirty state through `DirBlob` but file/symlink drops mostly delegate base drop.

Dependencies and integration points: central type returned by `FsBlobStore` and stored inside `ConcurrentFsBlobStore` cache.

Risks: type mismatch accessors return generic anyhow errors. Directory async drop can fail because it performs writeback, so cache drop paths must handle errors. Comments suggest possible ownership refactoring.

Test signals: parse dispatch tests, wrong-type accessor tests, directory writeback-on-drop tests, and invalid header tests are important.
