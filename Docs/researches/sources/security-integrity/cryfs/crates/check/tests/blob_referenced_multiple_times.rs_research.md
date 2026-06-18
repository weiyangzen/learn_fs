## sources/security-integrity/cryfs/crates/check/tests/blob_referenced_multiple_times.rs

Purpose: parameterized integration tests for blobs referenced by more than one directory entry. They verify both `BlobReferencedMultipleTimesError` and the corresponding root-node `NodeReferencedMultipleTimesError`, including cases where the duplicated blob is readable, unreadable, or missing.

Important APIs and helpers: local `make_file`, `make_dir`, and `make_symlink` create an initial blob in a chosen parent. `add_as_file_entry`, `add_as_dir_entry`, and `add_as_symlink_entry` add a second directory entry to the same blob id while declaring a potentially different entry type. `same_dir` and `different_dirs` parameterize whether duplicate references originate from one directory or two. `BlobStatus` selects normal, corrupted-root, or removed-blob setup.

Control flow and state: the test builds `FilesystemFixture::new_with_some_blobs`, creates one blob, records the root-node depth, adds a second reference, optionally corrupts or removes the blob, constructs expected `BTreeSet` reference sets, runs `run_cryfs_check`, and compares errors unordered. State persists in the in-memory encrypted blockstore through real fsblobstore directory-entry mutations.

Dependencies and integration: depends on `rstest`, `tokio`, `cryfs_check` error types, `BlobId`, `BlobType`, and common fixture APIs. It directly exercises the checker’s cross-index between directory blob references and data-tree root-node references.

Risks and test signals: TODOs document missing cycle-like directory-reference cases and mixed blob/node references. The test signal is strong for duplicate root-node reporting, including the important edge where unreadable or missing blobs still carry multiple logical references.
