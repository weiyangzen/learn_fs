# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/share.py

## Purpose
Represents a concrete immutable share on one server and performs lazy byte-range fetching, layout parsing, UEB validation, hash-tree validation, corruption reporting, and block delivery. `CommonShare` shares per-shnum block hash state across replicas.

## Important APIs, Types, And Functions
Exceptions are `LayoutInvalid` for malformed share layout and `DataUnavailable` for known-unavailable required bytes.

`Share(rref, server, verifycap, commonshare, node, download_status, shnum, dyhb_rtt, logparent)` stores remote bucket reference, server, verifycap-derived guessed offsets, actual offsets after parsing, pending/received/unavailable spans, requested block observers, and liveness.

`get_block(segnum)` returns an `EventStreamObserver` that will emit `COMPLETE`, `CORRUPT`, `DEAD`, or `BADSEGNUM`. Internal methods are organized into satisfaction (`_satisfy_offsets`, `_satisfy_UEB`, `_satisfy_share_hash_tree`, `_satisfy_block_hash_tree`, `_satisfy_ciphertext_hash_tree`, `_satisfy_data_block`), desire (`_desire_*`), and I/O (`_send_requests`, `_got_data`, `_got_error`, `_fail`).

`CommonShare` owns an authoritative or guessed block `IncompleteHashTree` for a share number. It exposes `set_authoritative_num_segments`, `need_block_hash_root`, `set_block_hash_root`, `get_desired_block_hashes`, `get_needed_block_hashes`, `process_block_hashes`, and `check_block`.

## Control Flow
`get_block()` queues observers for a segment and schedules the loop. The loop repeatedly consumes received data while it can satisfy prerequisites: parse version/offset table; fetch and validate UEB through `DownloadNode`; validate share hash chain; install block hash root; validate required block/ciphertext hash nodes; finally validate and deliver the data block.

If current data cannot satisfy progress, `_desire()` computes wanted and needed byte spans. Before actual offsets are known it may use guessed offsets when the server version tolerates immutable read overrun; otherwise it conservatively fetches version and offset table first. `_send_requests()` subtracts pending and already received spans, records block-request status events, and calls remote `read(start, length)`.

Received bytes move from `_pending` to `_received`; short reads mark remaining bytes as `_unavailable`. Required unavailable spans raise `DataUnavailable`. Corruption in layout, UEB, share hashes, or hash trees abandons the whole share and advises the server. Corrupt data blocks notify observers as `CORRUPT` but do not necessarily kill the share.

## State And Persistence
All state is in-memory. `DataSpans` stores received byte fragments until consumed; hash-tree state is retained in `DownloadNode` and `CommonShare` across block requests. The only persistence-like side effect is remote `advise_corrupt_share` notification to the storage server.

## Dependencies And Integration Points
Depends on remote bucket `read`, server version metadata, immutable layout offset conventions from `make_write_bucket_proxy`, `Spans`/`DataSpans`, `IncompleteHashTree`, hash utilities, `EventStreamObserver`, `DownloadStatus`, `DownloadNode` validation APIs, and states from `common.py`. `SegmentFetcher` consumes its observer events.

## Risks And Edge Cases
Guessed offsets plus overrun reads optimize round trips but require careful fallback when guesses are wrong. The file contains TODOs about empty share-hash sets, offset-section overlaps causing lost progress, over-requesting hash leaves, and leftover ciphertext hash data. Fatal share liveness after a single network/layout/hash failure may be conservative. `_satisfy_block_hash_tree()` computes corruption span size with `max(needed_hashes) * HASH_SIZE`, which is a diagnostic range rather than exact length.

## Test Signals
`src/allmydata/test/test_download.py` has extensive corruption and layout tests, including bad offset tables, block hashes, ciphertext hashes, share hashes, short reads, overrun behavior, and observer state transitions. `test_immutable.py` contains supporting mock hash-tree tests.
