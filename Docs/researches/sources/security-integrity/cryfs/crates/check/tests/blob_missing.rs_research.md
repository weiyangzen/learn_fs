# sources/security-integrity/cryfs/crates/check/tests/blob_missing.rs

Purpose: This integration test verifies that removing whole blobs causes `cryfs-check` to report the missing blob root node and any orphaned descendants correctly.

Important APIs and flow: The parameterized `blob_entirely_missing` test selects file, directory with children, empty directory, symlink, or rootdir-with-children blobs from `SomeBlobs`. It records descendant blobs if the selected blob is a directory, removes the blob by id through `update_fsblobstore`, builds expected `NodeMissingError` plus expected unreferenced-root-node errors for orphaned descendants, runs `run_cryfs_check`, and compares unordered errors. A second test removes an otherwise childless root dir and expects one root `NodeMissingError`.

State and persistence: Tests mutate a temporary filesystem fixture by removing blobs from the fsblobstore, then run the checker over the persisted corrupted state.

Dependencies and integration: It uses `rstest`, `FilesystemFixture`, `SomeBlobs`, entry helper expectations, `RemoveResult`, `BlobReference`, `BlobReferenceWithId`, `NodeAndBlobReference`, and `NodeMissingError`.

Risks and test signals: The tests establish that a missing blob is modeled as a missing root data node (`blob_id.to_root_block_id()`). The file notes that combined blob-missing and referenced-multiple-times coverage lives in the blob referenced multiple times test module.
