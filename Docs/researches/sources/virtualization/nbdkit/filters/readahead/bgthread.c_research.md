# File Research: sources/virtualization/nbdkit/filters/readahead/bgthread.c

This file implements the per-connection readahead background thread. The thread waits on a condition variable until commands are present, removes the first queued command, and handles `CMD_QUIT` or `CMD_CACHE`.

`CMD_CACHE` invokes the underlying plugin's `.cache` callback for the queued offset/count and ignores errors because readahead is advisory and there is no client response path. `CMD_QUIT` exits the thread after all earlier queued commands have been processed.

The command queue is protected by the control mutex. The thread assumes command construction and `next` lifetime are managed by `readahead.c`.
