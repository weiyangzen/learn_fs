# sources/security-integrity/cryfs/crates/check/src/node_info/blob_reference.rs

Purpose: `BlobReference` records how a blob is referenced by a parent directory entry.

Important APIs and flow: The struct contains `blob_type`, `parent_id`, and absolute `path`. `root_dir()` constructs the synthetic root reference as a directory with zero parent id and root path.

State and persistence: It is immutable reference context used in checker state, errors, and display output.

Dependencies and integration: It depends on `BlobId`, `BlobType`, and `AbsolutePathBuf`. It is embedded in `BlobReferenceWithId`, `MaybeBlobReferenceWithId`, blob errors, and parent-pointer checks.

Risks and test signals: Root uses `BlobId::zero()` as a sentinel parent, so consumers must understand that root's parent is synthetic.
