# sources/security-integrity/cryfs/crates/check/src/checks/blobs_readable.rs

Purpose: This check reports reachable blobs that could not be loaded at all. It does not verify every underlying data node; the file explicitly notes that it only catches whole-blob load failures.

Important APIs and flow: `CheckBlobsReadable` stores `unreadable_blobs: BTreeMap<BlobId, BTreeSet<BlobReference>>`. `process_reachable_blob` records `BlobToProcess::Unreadable`, `process_reachable_blob_again` delegates to the same path so duplicate references are accumulated, node callbacks do nothing, and `finalize` emits one `BlobUnreadableError` per unreadable id.

State and persistence: State is in-memory aggregation keyed by `BlobId`. A `BTreeMap`/`BTreeSet` gives deterministic ordering for errors and display tests.

Dependencies and integration: It implements `FilesystemCheck` and is included in `AllChecks`. It depends on `BlobToProcess`, `BlobReference`, and `BlobUnreadableError`.

Risks and test signals: It relies on the runner to classify unreadable blobs correctly. It intentionally does not inspect partial readability, so node-level unreadability is covered by `unreferenced_nodes` and runner traversal instead.
