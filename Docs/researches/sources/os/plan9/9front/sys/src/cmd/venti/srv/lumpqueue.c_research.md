# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/lumpqueue.c

`lumpqueue.c` provides asynchronous write queues for Venti lumps. It allocates one small ring queue per index section, starts a `queueproc` worker for each, and routes writes by `indexsect(mainindex, score)` so writes for the same section serialize through the same queue.

`queuewrite()` enqueues a `Lump`, `Packet`, creator, timestamp, and generation, sleeping when the ring is full. `flushqueue()` bumps the global generation and waits until all older queued writes drain. Workers call `writeqlump()` and then `putlump()`.

The queue depth is intentionally tiny (`MaxLumpQ` 8), so this is latency overlap rather than large buffering. The generation mechanism is the main ordering contract used by sync requests.
