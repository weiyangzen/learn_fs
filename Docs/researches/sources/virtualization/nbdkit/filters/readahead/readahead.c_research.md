# File Research: sources/virtualization/nbdkit/filters/readahead/readahead.c

This filter issues asynchronous cache hints after sequential reads. It maintains a global adaptive window between 32 KiB and 4 MiB, plus global `last_offset` and `last_readahead` guarded by `window_lock`. It records the final server thread model in `.get_ready`.

Each connection creates a background thread and command queue in `.open`, then sends a quit command and joins the thread in `.close`. The filter only works when the underlying stack advertises `NBDKIT_CACHE_NATIVE` and the final thread model is `PARALLEL`; otherwise `.can_cache` logs a warning and may suggest adding the cache filter.

On `.pread`, if working, it computes a cache command starting immediately after the synchronous read, clips it to backend size, adapts the window based on forward progress, queues the command for the background thread, and then performs the actual synchronous read. The asynchronous `.cache` request is best-effort and not reported to the client.

The main correctness dependency is thread-model compatibility: the background thread calls into `next->cache` concurrently with normal reads, so the filter refuses to be useful unless the final stack is parallel-safe and cache-native.
