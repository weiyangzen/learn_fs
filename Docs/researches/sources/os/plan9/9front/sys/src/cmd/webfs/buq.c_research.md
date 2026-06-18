# File Research: sources/os/plan9/9front/sys/src/cmd/webfs/buq.c

Bounded queue implementation connecting 9p reads/writes to HTTP worker streams in `webfs`.

Key behavior:
- `Buq` stores buffered byte chunks, blocked write requests, queued read/open requests, response URL/header metadata, close/error state, and a rendezvous for backpressure.
- `buwrite()` appends data and sleeps when queued bytes exceed the limit.
- `buread()` blocks until data or closure, consumes bytes, wakes writers, and returns queued errors as read failures.
- `bureq()` adapts 9p `Tread`, `Twrite`, and `Topen` requests into the queue, responding immediately when possible or queueing the request.
- `matchreq()` pairs pending reads/opens with buffered data or closure; `kickwqr()` releases queued write requests when data is consumed or the queue closes.
- `buflushreq()` interrupts queued 9p reads/opens or flushes queued writes.

Notable dependencies:
- Plan 9 libthread locking/rendezvous and lib9p `Req`.
- `Url` and `Key` metadata from `dat.h`.

Research notes:
- The queue is reference-counted; `bufree()` owns queued buffers, URL, headers, and error text.
- Queued writes initially point into the request payload and are compacted into owned buffers when accepted.
