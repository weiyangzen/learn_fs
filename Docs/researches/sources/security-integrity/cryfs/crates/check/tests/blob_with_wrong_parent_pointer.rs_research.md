## sources/security-integrity/cryfs/crates/check/tests/blob_with_wrong_parent_pointer.rs

Purpose: validates detection of blobs whose stored parent pointer disagrees with the directory entries that reference them. It also checks interaction with multiple references.

Important APIs and functions: `make_file`, `make_symlink`, `make_empty_dir`, and `make_large_dir` create target blobs and parent directories. `set_parent` loads a blob through `FsBlobStore` and calls `set_parent` to change its embedded parent id. Three tests cover one, two, and four directory references.

Control flow and state: each test creates old parent(s), creates a blob under one old parent, creates an unrelated new parent, mutates the blob parent pointer to the new parent, and expects `WrongParentPointerError`. Multi-reference tests also expect `NodeReferencedMultipleTimesError` for the root node and `BlobReferencedMultipleTimesError` with readable blob info carrying the wrong parent pointer.

Dependencies and integration: integrates directory-entry metadata (`BlobReference` path, parent id, declared `BlobType`) with blob-internal parent pointers. It depends on `NonZeroU8` depth conversion for root-node info and `BTreeSet` to make reference order irrelevant.

Risks and test signals: it is strong for parent-pointer mismatch plus duplicate-reference composition. It intentionally creates references with file, dir, and symlink entry types, testing that the checker reports what the directory says and what the blob header says rather than silently normalizing inconsistencies.
