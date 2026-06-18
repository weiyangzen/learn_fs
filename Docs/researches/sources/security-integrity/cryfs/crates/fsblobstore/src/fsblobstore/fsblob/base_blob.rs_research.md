# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/base_blob.rs

Purpose: `BaseBlob` is the common typed-header wrapper over a raw `BlobStore::ConcreteBlob`.

Important APIs/types/functions: `parse` reads and validates the fsblob header. `try_create_with_id` and `create` build a new header plus payload. Accessors expose blob id, type, parent, data length, data read/write/resize, flush, removal, and block enumeration. Test-only helpers expose node counts and raw blobs.

Control flow: parsing reads exactly the header, checks `FORMAT_VERSION_HEADER`, caches the header view, then typed wrappers inspect `blob_type`. Creation writes a fully formed `fsblob` layout and caches only the header. Data operations offset all reads/writes past the header.

State and persistence behavior: persistent layout is `format_version_header`, `blob_type`, `parent`, then type-specific data. `set_parent` updates both storage and cache. `read_all_data` rejects blobs too small for a header.

Dependencies and integration points: used by `FileBlob`, `DirBlob`, and `SymlinkBlob`; depends on `binary_layout`, `cryfs_blobstore`, `cryfs_blockstore`, and `cryfs_utils::Data`.

Risks: error paths call `async_drop().await.unwrap()` in several places. Header validation does not verify parent consistency beyond storing the pointer. `num_data_bytes` subtracts header size and would underflow only if lower layers reported an invalid smaller blob.

Test signals: important tests are format-version rejection, data offset correctness, parent update persistence, and remove/flush delegation.
