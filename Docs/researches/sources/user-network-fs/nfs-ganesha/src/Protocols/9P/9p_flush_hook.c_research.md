## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_flush_hook.c

Purpose: provides the synchronization machinery behind 9P `TFLUSH`.

APIs and flow: `_9p_AddFlushHook` inserts a request hook into a tag-hash bucket; `_9p_FlushFlushHook` finds an older hook with the target tag, attaches a stack-local condition object, removes the hook, waits for request completion, then returns to let `RFLUSH` be sent; `_9p_DiscardFlushHook` removes the hook or signals the waiting flusher once the request reply path has completed.

State/dependencies: state lives in `struct _9p_conn` flush buckets guarded by pthread mutexes and glists. The flush condition is transient but shared between the flushing thread and request-completion thread while the bucket lock coordinates lifetime.

Risks/tests: concurrency risks include missed signals, stack condition lifetime, hook deletion races, and tag modulo bucket correctness. Stress tests should cover simultaneous flushes, request completion during wait setup, and same tag with sequence ordering.
