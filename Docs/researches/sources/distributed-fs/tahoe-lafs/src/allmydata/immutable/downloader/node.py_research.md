# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/node.py

## Purpose
Central immutable ciphertext download coordinator. `DownloadNode` owns shared per-file download state, discovers shares, validates UEB/hash trees, fetches segments, decodes erasure-coded blocks, checks ciphertext hashes, and feeds `Segmentation` readers.

## Important APIs, Types, And Functions
`IDownloadStatusHandlingConsumer` is an interface for consumers that can receive `DownloadStatus` read-event/status handles. `Cancel` is a small active flag plus callback used for cancelable segment requests.

`DownloadNode(verifycap, storage_broker, secret_holder, terminator, history, download_status)` initializes guessed segment tables, shared `share_hash_tree`, `ciphertext_hash_tree`, `ShareFinder`, known shares, request queues, and logging.

External methods are `read(consumer, offset, size)`, `get_segment(segnum, logparent=None)`, `get_segsize()`, and `stop()`. Share/fetcher callbacks include `got_shares`, `no_more_shares`, `validate_and_store_UEB`, `process_share_hashes`, `process_ciphertext_hashes`, `want_more_shares`, `fetch_failed`, and `process_blocks`.

## Control Flow
Construction guesses segment size from `DEFAULT_IMMUTABLE_MAX_SEGMENT_SIZE` and verifycap parameters so initial reads can speculatively fetch data before UEB metadata is known. `read()` clips ranges, records status, creates a `Segmentation` producer, and delegates range-to-segment sequencing.

`get_segment()` appends a cancelable segment request and starts a `SegmentFetcher` if none is active. Only one active segment fetch runs per node. Existing live shares are offered to each new fetcher, and the fetcher asks `ShareFinder` for more when needed.

When any share provides a valid UEB, `validate_and_store_UEB()` checks the UEB hash against the verifycap, parses actual segment/block/tail sizes, configures CRS decoder and authoritative hash trees, seeds ciphertext/share roots, fires segment-size observers, and updates `ShareFinder` common-share sizes.

`process_blocks()` decodes `k` validated blocks using `CRSDecoder`, trims tail padding, validates the ciphertext segment hash against the ciphertext Merkle tree, records status events, and delivers `(offset, segment, decodetime)` to all queued requests for that segment. Failures are delivered to all matching request Deferreds.

## State And Persistence
State is in-memory and shared across reads of the same `CiphertextFileNode`: UEB knowledge, segment size, hash trees, known `Share` objects, current active segment, queued segment requests, and status events. It registers with an optional terminator so shutdown can stop active fetches and share finding. No durable state is written.

## Dependencies And Integration Points
Depends on CHK verifycaps, `CRSDecoder`, `IncompleteHashTree`, `hashutil`, `mathutil`, `observer.OneShotObserverList`, downloader `ShareFinder`, `SegmentFetcher`, `Segmentation`, and status/history objects. It is created lazily by `CiphertextFileNode` in `filenode.py`.

## Risks And Edge Cases
The guessed segment-size path can fetch a wrong segment for nonzero offsets and relies on `Segmentation` retry after UEB discovery. Only one active segment fetch can serialize concurrent reads for different segments. `validate_and_store_UEB()` notes malformed authentic UEBs can still throw assertions. `no_more_shares()` sets `_no_more_shares` without initialization in `__init__`, relying on dynamic attribute creation. Hash-tree failures after successful share validation are considered severe and become `BadCiphertextHashError`.

## Test Signals
`src/allmydata/test/test_download.py` exercises range reads, wrong-segment retry, bad segment numbers, corrupt hash trees, decode failures, status accounting, and segment fetch orchestration. `test_system.py` and filenode tests cover integration through immutable nodes.
