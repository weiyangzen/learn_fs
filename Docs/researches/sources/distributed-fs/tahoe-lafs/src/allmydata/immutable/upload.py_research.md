# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/upload.py

## Purpose

This module is the main immutable upload orchestration layer for Tahoe-LAFS. It turns user-provided uploadables into literal caps for tiny files or CHK immutable files for larger files. For CHK uploads it handles encryption, storage-index derivation, encoding parameter setup, peer/server selection using servers-of-happiness, remote bucket allocation, encoder wiring, upload status/results, helper-assisted upload client behavior, and uploadable wrappers for file handles, filenames, and in-memory data.

## Important APIs, Types, and Functions

- Eliot fields/actions/messages (`LOCATE_ALL_SHAREHOLDERS`, `GET_SHARE_PLACEMENTS`, `CONVERGED_HAPPINESS`) record peer-selection decisions.
- `TooFullError` marks full-server allocation responses internally.
- `HelperUploadResults` is the Foolscap-compatible result object exchanged with older/newer helpers. Its shape is compatibility-sensitive.
- `UploadResults` implements `IUploadResults` and stores file size, helper ciphertext bytes, preexisting/pushed shares, share/server maps, timings, UEB data/hash, verify cap string, and final read URI.
- `ServerTracker` wraps one storage server for a specific upload. It computes allocated share size with `layout.make_write_bucket_proxy`, asks for existing buckets, allocates buckets, wraps returned bucket writers in layout proxies, and aborts partial buckets.
- `PeerSelector` tracks writeable/read-only/bad peers, preexisting shares, computes share placements via `happiness_upload.share_placement`, and calculates happiness.
- `_QueryStatistics` tracks allocation query totals, good/bad/full/error/contacted counts.
- `Tahoe2ServerSelector` drives the server-selection algorithm and returns `(upload_trackers, already_serverids)`.
- `_Accum` and `EncryptAnUploadable` adapt an `IUploadable` plaintext source into an `IEncryptedUploadable` ciphertext source while computing plaintext hashes and storage index.
- `UploadStatus` implements `IUploadStatus` with storage index, size, helper flag, status string, three progress channels, active flag, results, and a monotonic counter.
- `CHKUploader` runs direct CHK uploads using `encode.Encoder`, `Tahoe2ServerSelector`, and storage bucket writers.
- `read_this_many_bytes` repeatedly reads from an uploadable until a requested byte count is reached.
- `LiteralUploader` builds literal file URIs and upload results for tiny files.
- `RemoteEncryptedUploadable` exposes an encrypted uploadable over Foolscap for helper-assisted uploads and supports forward-only reads with hash-only skipping.
- `AssistedUploader` is the client-side helper upload coordinator.
- `BaseUploadable`, `FileHandle`, `FileName`, and `Data` implement uploadable sources and convergent/random encryption-key generation.
- `Uploader` is the `IUploader` service entry point used by the Tahoe client.

## Control Flow

Top-level upload starts in `Uploader.upload`. It requires a running service with a parent client, gets the source size, applies default encoding parameters from the parent, counts stats, then chooses a path. Files at or below `URI_LIT_SIZE_THRESHOLD` go to `LiteralUploader`, which reads all bytes and returns a `LiteralFileURI` result. Larger files are wrapped in `EncryptAnUploadable`. If a helper connection is available, `AssistedUploader` first computes the storage index and contacts the helper; otherwise `CHKUploader` performs direct upload locally. In both CHK cases, the final callback combines the verify cap from upload results with the encryption key to produce the read cap URI.

Direct CHK upload flow is `CHKUploader.start` -> `start_encrypted`. It creates an `encode.Encoder`, attaches the encrypted uploadable, asks `locate_all_shareholders` to select/allocate buckets, passes bucket writers and preexisting share map into the encoder, starts encoding, and converts the returned verify cap into `UploadResults`. `locate_all_shareholders` extracts encoder parameters, creates `Tahoe2ServerSelector`, and passes storage index, share/block/segment counts, happiness, and UEB size.

Server selection in `Tahoe2ServerSelector.get_shareholders` first creates trackers for up to `2 * total_shares` candidate servers. It filters writeable servers by `maximum-immutable-share-size`; oversized-incompatible servers become read-only candidates. It asks read-only and writeable trackers about existing shares with 15-second timeouts. Then it repeatedly computes share placements, asks trackers to allocate assigned shares, updates homeless/preexisting/use-tracker state, marks failed/full servers read-only, merges preexisting and newly allocated shares, and stops when effective happiness reaches the requested minimum or no progress remains. On failure it aborts allocated buckets and raises `UploadUnhappinessError`; on success it returns trackers holding allocated shares plus preexisting share locations.

Encryption flow in `EncryptAnUploadable` obtains encoding parameters and size, derives an AES key from either convergent hashing or random uploadable key generation, computes the storage index as a hash of the key, and services `read_encrypted(length, hash_only)` by repeatedly reading plaintext chunks up to `CHUNKSIZE`. Every plaintext chunk updates whole-file and per-segment hashers and advances the AES-CTR encryptor. In hash-only mode it still encrypts to advance the counter but discards ciphertext.

Assisted upload flow in `AssistedUploader` gets size/encoding parameters, calls remote helper `upload_chk(storage_index)`, and either accepts already-present helper results or creates `RemoteEncryptedUploadable` and calls the returned helper's `upload`. It validates returned UEB parameters, builds a verify cap, converts helper server IDs to local stub server objects, and returns normal `UploadResults`.

## State and Persistence Behavior

`Uploader` stores helper connection state, stats/history hooks, and weak references to active uploaders. `UploadStatus` is mutable in-memory progress state; status progress indexes are `[0]` convergence/storage-index work, `[1]` ciphertext/encryption/fetching, and `[2]` encode/push. `CHKUploader` stores its encoder, upload status, storage index, timing fields, and per-share server tracker mapping. `Tahoe2ServerSelector` stores peer-selection state during one upload: peer selector, homeless shares, preexisting shares, servers with shares, trackers selected for use, query statistics, and last failure.

Persistent effects for CHK uploads are remote immutable shares allocated and written via storage server `allocate_buckets` and layout bucket writers. `ServerTracker.abort` attempts to remove partial remote buckets after selection failure. `FileHandle` caches file size and encryption key; convergent key generation rewinds and scans the source file. `FileName.close` closes the owned file handle; `FileHandle.close` intentionally leaves externally-owned handles open; `Data` wraps a `BytesIO`.

## Dependencies and Integration Points

The module depends on Twisted `Deferred`s/services, Foolscap remote objects, Tahoe crypto/hash utilities, URI classes, storage server wrappers, `encode.Encoder`, immutable share `layout`, happiness utilities, server broker APIs, and interfaces including `IUploadable`, `IUploader`, `IEncryptedUploadable`, `RIEncryptedUploadable`, `IUploadStatus`, and `IPeerSelector`. `offloaded.py` subclasses `CHKUploader` and consumes/produces `HelperUploadResults`; `repairer.py` reuses `CHKUploader` by presenting a file node as `IEncryptedUploadable`; `literal.py` consumes literal caps created by `LiteralUploader`; storage and checker/downloader layers consume the remote shares and verify caps generated here.

## Risks and Edge Cases

- `Tahoe2ServerSelector.__init__` initializes `_query_stats`, but `get_shareholders` assigns `_query_status`; the existing `_query_stats` remains in use, so the intended reinitialization may be a typo and stale stats would matter if a selector instance were reused.
- Server selection mutates tracker lists inside asynchronous callbacks. The code assumes Twisted callback serialization, but changes to concurrency or data structures could affect placement/retry behavior.
- Read-only servers are still queried to renew existing shares; this is intentional but easy to break if allocation calls are optimized away.
- `PeerSelector.mark_readonly_peer` removes from `peers` without guarding membership; callers currently add peers first, but future paths must preserve that order.
- `EncryptAnUploadable` must encrypt even in `hash_only` mode to advance AES-CTR state. Replacing the crypto backend or adding seek support must preserve counter alignment for helper forward skips.
- `_hash_and_encrypt_plaintext` computes progress as bytes read divided by file size; zero-sized CHK files are avoided by literal upload threshold, but any alternate path should avoid division by zero.
- `read_this_many_bytes` asserts every read returns at least one byte until the requested size is satisfied; uploadables with premature EOF will assert rather than return a structured error.
- `LiteralUploader` reads the entire tiny file into memory, which is acceptable only because `Uploader` gates it by size.
- Helper result compatibility is fragile: `HelperUploadResults` must not change existing field shapes because helpers and clients may be different versions.
- `Uploader.upload` closes the uploadable in an `addBoth` callback, so caller-owned uploadables must implement close semantics carefully; `FileHandle` intentionally does not close external handles.

## Test Signals

`src/allmydata/test/test_upload.py` is the primary suite for uploadable wrappers, encryption behavior, server selection, happiness behavior, assisted/direct upload results, and `EncryptAnUploadable` edge cases including known ciphertext and large requested reads. `test_helper.py` covers helper interaction through `AssistedUploader` and `offloaded.Helper`. `test_encode.py` exercises encoder integration with encrypted uploadables. `test_storage.py` validates layout bucket writer/reader assumptions used by `ServerTracker`. `test_repairer.py` covers the repair path that reuses `CHKUploader`.
