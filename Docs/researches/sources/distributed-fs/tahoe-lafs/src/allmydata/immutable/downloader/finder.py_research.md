# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/finder.py

## Purpose
Finds immutable shares by asking storage servers for buckets for a storage index. It feeds discovered `Share` objects to the download node on demand and manages pending/overdue DYHB requests.

## Important APIs, Types, And Functions
`incidentally(res, f, *args, **kwargs)` is a Deferred-chain helper that performs side effects while preserving the original result. `RequestToken` wraps a server for pending request tracking.

`ShareFinder(storage_broker, verifycap, node, download_status, logparent=None, max_outstanding_requests=10)` tracks server iterator, pending/overdue requests, timers, and per-shnum `CommonShare` objects.

Important methods are `start_finding_servers()`, `hungry()`, `loop()`, `send_request(server)`, `_got_response()`, `_create_share()`, `_deliver_shares()`, `_got_error()`, `overdue()`, `_request_retired()`, `update_num_segments()`, and `stop()`.

## Control Flow
The finder is lazy: it does not fetch the server iterator until `hungry()` is called. The loop sends parallel `get_buckets(storage_index)` requests while hungry and below the non-overdue outstanding limit. Each request records a `DownloadStatus` DYHB event and installs an overdue timer. Responses create `Share` instances for returned buckets, reusing or creating one `CommonShare` per share number, then deliver shares to the node and clear hunger. If all servers and pending requests are exhausted, it eventually calls `share_consumer.no_more_shares()`.

## State And Persistence
All state is transient. `CommonShare` instances preserve per-share block hash tree knowledge across multiple `Share` instances and servers for the same shnum. `stop()` cancels overdue timers and disables further looping.

## Dependencies And Integration Points
Depends on the storage broker server ordering (`get_servers_for_psi`), server storage APIs (`get_storage_server().get_buckets`), downloader `Share` and `CommonShare`, Twisted reactor timers, Foolscap eventual scheduling, and `DownloadStatus` event APIs. `DownloadNode.want_more_shares()` drives `hungry()`.

## Risks And Edge Cases
Overdue requests remain pending but stop counting toward the outstanding limit, allowing more server probes under latency. `stop()` cancels timers but does not cancel remote Deferreds. `update_num_segments()` asserts authoritative segment count, so it must be called only after UEB validation. Server iterator exhaustion plus hanging requests can delay `no_more_shares()`.

## Test Signals
`src/allmydata/test/test_immutable.py` includes `TestShareFinder`. Downloader and hung-server tests exercise overdue handling, max outstanding requests, and no-more-shares integration.
