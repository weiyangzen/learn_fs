# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/log.c

Implements an asynchronous ring-buffer log for factotum’s `/mnt/factotum/log`. Readers are queued in `Logbuf.wait`; log messages are delivered as they arrive.

`logbufproc` pairs waiting reads with queued messages, truncating safely when the caller’s buffer is too small and avoiding cutting UTF-8 continuation bytes before appending `...\n`. `logbufflush` interrupts queued reads.

`flog` formats into a fixed 1024-byte stack buffer and appends to the global `logbuf`; if global `debug` is enabled, log entries are also printed to stderr.
