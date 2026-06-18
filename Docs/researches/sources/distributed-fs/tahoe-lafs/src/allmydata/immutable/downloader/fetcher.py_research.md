# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/fetcher.py

## Purpose
`SegmentFetcher` obtains enough validated share blocks to reconstruct one ciphertext segment. It chooses shares, balances server diversity, handles overdue/failed/corrupt shares, and reports either `process_blocks()` or `fetch_failed()` to its parent `DownloadNode`.

## Important APIs, Types, And Functions
`SegmentFetcher(node, segnum, k, logparent)` tracks unused shares sorted by DYHB RTT and shnum, outstanding shares per server, active share per shnum, overdue shares, observers, completed blocks, and no-more-shares state.

Public callbacks from the parent are `add_shares(shares)`, `no_more_shares()`, and `stop()`. Internal scheduling is `loop()`/`_do_loop()`, `_find_and_use_share()`, `_start_share()`, `_ask_for_more_shares()`, `_cancel_all_requests()`, and `_block_request_activity()`.

## Control Flow
When shares arrive, they are sorted and the loop is eventually scheduled. The loop first checks whether the requested segment is valid if the node has authoritative segment count. It then sends block requests until the union of completed and active share numbers reaches `k`. It prefers one share per server, increases `_max_shares_per_server` if diversity is blocking progress, and asks `DownloadNode.want_more_shares()` when more candidates are needed.

Share observers emit `COMPLETE`, `OVERDUE`, `CORRUPT`, `DEAD`, or `BADSEGNUM`. Complete blocks are retained by share number. Overdue requests are removed from active accounting but can still complete. Terminal states retire the share from observer/server maps. When at least `k` blocks are complete, the fetcher stops and calls `node.process_blocks(segnum, blocks)`. If no possible set can reach `k`, `_no_shares_error()` raises `NoSharesError` or `NotEnoughSharesError` through `node.fetch_failed()`.

## State And Persistence
All state is in-memory per segment fetch. `stop()` cancels outstanding `EventStreamObserver`s and deletes large tracking structures to help garbage collection. Completed block data lives only long enough for `DownloadNode` to decode the segment.

## Dependencies And Integration Points
Depends on Foolscap `eventually`, Twisted `Failure`, Tahoe `NotEnoughSharesError`/`NoSharesError`, `DictOfSets`, logging, and states from `common.py`. It consumes `Share.get_block()` observers and calls `DownloadNode` methods.

## Risks And Edge Cases
The diversity algorithm can increase requests per server when necessary, trading reliability/latency against server concentration. Overdue requests are not canceled and can still affect completion. A bad segment number is handled on the next loop after authoritative segment metadata is known. Exceptions in the loop are converted to parent fetch failure and then re-raised, so tests need eventual-error handling.

## Test Signals
`src/allmydata/test/test_download.py` has a dedicated `SegmentFetcher` test cluster around share selection, overdue behavior, diversity growth, failures, and no-shares/not-enough-shares handling. Hung-server behavior is also covered in `test_hung_server.py`.
