# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/offloaded.py

## Purpose

This module implements the helper-server side of assisted CHK immutable uploads. A client-side `AssistedUploader` can ask a remote helper whether a CHK file is already fully present in the grid; if not, the helper fetches encrypted ciphertext from the client, stores it in resumable local staging files, and runs the normal CHK upload pipeline from the helper node. This offloads peer selection, erasure encoding, and share pushing from the client while preserving the same immutable cap results.

## Important APIs, Types, and Functions

- `NotEnoughWritersError` reports that all assisted upload readers failed.
- `CHKCheckerAndUEBFetcher` checks storage servers for all shares of a storage index and fetches one URI extension block. It returns `False` or `(sharemap, ueb_data, ueb_hash)`.
- `CHKUploadHelper` implements `RICHKUploadHelper` and subclasses `upload.CHKUploader`. It is a Foolscap `Referenceable` used by clients after `Helper.remote_upload_chk`.
- `AskUntilSuccessMixin` manages a list of remote readers and retries `callRemote` operations against the next reader when one fails.
- `CHKCiphertextFetcher` pulls encrypted bytes from one or more remote `RIEncryptedUploadable` readers into `CHK_incoming/<si>`, then atomically renames to `CHK_encoding/<si>` when complete.
- `LocalCiphertextReader` implements `IEncryptedUploadable` over the helper's local ciphertext file and proxies encoding parameters/close to the original reader.
- `Helper` implements `RIHelper` and `IStatsProducer`; it handles `remote_upload_chk`, tracks active uploads, counters, stats, and on-disk helper staging directories.

## Control Flow

`Helper.remote_upload_chk(storage_index)` increments counters and first deduplicates active uploads. If no upload is active, `_check_chk` uses `CHKCheckerAndUEBFetcher` to ask storage servers for existing buckets and fetch a UEB through `ReadBucketProxy`. If all `total_shares` are found and a UEB is available, the helper returns a `HelperUploadResults` object and no upload helper. Otherwise `_did_chk_check` creates or returns a `CHKUploadHelper` for the storage index.

`CHKUploadHelper` wires together three phases in its constructor: wait for `CHKCiphertextFetcher.when_done`, start `LocalCiphertextReader`, then run inherited `start_encrypted`. `remote_upload(reader)` registers the client reader with both the fetcher and local reader and returns a deferred that fires when `_finished_observers` fires. `_finished` converts normal `UploadResults` into `HelperUploadResults`, translating server objects into server IDs, closes the local reader, deletes the completed encoding file, notifies helper completion, and fires observers. `_failed` logs, fires failure, and removes the active upload.

`CHKCiphertextFetcher` starts once a reader is added. It resumes from an existing incoming file if present, bypasses fetching if the encoded file already exists, otherwise calls remote `get_size`, opens the incoming file in append mode, and repeatedly calls remote `read_encrypted(offset, CHUNK_SIZE)`. It writes returned chunks, updates counters/status, and when complete renames incoming to encoding. `AskUntilSuccessMixin.call` retries failed remote calls with remaining readers and raises `NotEnoughWritersError` if none remain.

## State and Persistence Behavior

`Helper` creates and maintains `CHK_incoming` and `CHK_encoding` under its base directory. Incoming files are partial ciphertext and enable resumable fetch after interrupted helper/client activity. Encoding files represent complete ciphertext ready for local erasure encoding and upload. Active uploads live in `_active_uploads` keyed by storage index, while `_all_uploads` is a weak dictionary for debugging/history. Stats include active upload count, incoming/encoding file counts and bytes, age-over-48h byte totals, and upload/fetch counters.

`CHKUploadHelper` stores transient upload status, storage index, file paths, reader/fetcher objects, timing data, and completion observers. `CHKCiphertextFetcher` tracks the reader list, open output file, expected/have bytes, cumulative fetch time, total time, and fetched byte count. Completed encoding files are deleted after successful upload; failed or interrupted files may remain for later resume or cleanup.

## Dependencies and Integration Points

The module depends on Foolscap `Referenceable`, `DeadReferenceError`, and `eventually`; Twisted deferreds; Tahoe upload classes/results; `ReadBucketProxy` for UEB fetching; storage broker server enumeration; URI extension packing/unpacking; `hashutil.uri_extension_hash`; `fileutil.make_dirs`; and Tahoe stats/history/logging utilities. Client-side integration is `upload.AssistedUploader`, which calls helper `upload_chk` and then invokes the returned `RICHKUploadHelper.upload` with a `RemoteEncryptedUploadable`. The helper reuses `upload.CHKUploader`, so server selection, layout writing, and encoder behavior remain shared with direct uploads and repairs.

## Risks and Edge Cases

- Existing complete encoding files bypass fetching. This supports resume but depends on file naming by storage index and assumes prior file contents are correct for that SI.
- Partial incoming files resume by byte count without local cryptographic validation until later encoding/checking stages. Bad partial files can waste work or fail later.
- `AskUntilSuccessMixin` retries any remote call against the next reader, but non-idempotent interactions need scrutiny; current uses are size, encoding parameters, ciphertext reads, and close.
- `_got_response` records all bucket references from all servers; `_get_uri_extension` pops one arbitrary reader and treats UEB fetch failure as file unavailable rather than trying every reader.
- `_done` in `CHKCheckerAndUEBFetcher` requires all `total_shares`, not merely `needed_shares`, to declare the file already present. This is conservative and may force unnecessary upload work for recoverable but not perfectly healthy files.
- `LocalCiphertextReader.close` forwards `close` to one remote reader; the comment questions whether forwarding makes sense.
- Staging directories can accumulate old incoming/encoding files after failures; `get_stats` reports old bytes, but cleanup behavior is external.

## Test Signals

`src/allmydata/test/test_helper.py` directly exercises assisted uploads, concurrent uploads, failed previous uploads/resume behavior, already-uploaded detection, and fake `CHKUploadHelper`/checker injection. `test_system.py` adjusts `CHKCiphertextFetcher.CHUNK_SIZE` in integration scenarios. Upload result conversion and helper protocol compatibility are also indirectly exercised by `test_upload.py` assisted-upload paths.
