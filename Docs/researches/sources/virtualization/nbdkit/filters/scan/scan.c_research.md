# File Research: sources/virtualization/nbdkit/filters/scan/scan.c

This file implements the public nbdkit `scan` filter callbacks. The filter opportunistically warms the backing cache by running a per-connection background thread that sends `NBD_CMD_CACHE` requests, with configurable scan direction behavior through `scan-ahead`, `scan-clock`, `scan-forever`, and `scan-size`.

Key control flow: configuration validates `scan-size` as a power of two in `[512..32M]`; `.get_ready` records the final server thread model; `.open` tracks whether the connection is for the default export; `.prepare` only starts scanning when the default export is used, the final thread model is `NBDKIT_THREAD_MODEL_PARALLEL`, and the underlying layer advertises `NBDKIT_CACHE_NATIVE`; `.pread` can enqueue a `CMD_NOTIFY_PREAD` command with the next offset before forwarding the read.

Important state is per connection in `struct scan_handle`: default-export flag, thread-running flag, pthread id, and `bgthread_ctrl`. The background command queue is protected by a mutex and uses the vector helpers declared in `scan.h`.

Risks and invariants: scanning is deliberately disabled for non-default exports, non-parallel backends, and non-native cache support. Queue append failures in `.pread` return failure before the real read. Thread shutdown depends on sending `CMD_QUIT`, joining the thread, destroying the mutex, and resetting the vector exactly once.
