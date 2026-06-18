## sources/user-network-fs/blobfuse2/component/xload/threadpool.go

Purpose: Generic xload worker pool with separate priority and regular queues for lister, splitter, and data manager stages.

Important APIs and flow: `NewThreadPool` validates worker count and callback, then creates buffered priority and regular channels. `Start` stores the context and launches workers, reserving 10% for priority-only reads. `Schedule` checks context cancellation and sends priority items to `priorityItems`, otherwise regular work to `workItems`. `Do` loops until context cancellation or channel closure; regular workers select from both queues. `process` invokes the callback, logs errors, and returns the item with error/data length on a response channel when one is configured.

State and dependencies: State is worker count, wait group, queues, callback, and context. It integrates into every `XComponent`.

Risks: `cap(item.ResponseChannel)` panics if `ResponseChannel` is nil; current callers appear to provide it for response paths and omit it for fire-and-forget, making this a latent bug because nil channel cap is allowed in Go, but sending would block only when cap > 0. Scheduling after channel close can panic. Tests cover creation, start/stop, schedule, and priority throughput.
