# File Research: sources/virtualization/nbdkit/filters/scan/bgthread.c

This file implements the scan filter's background cache-scanning thread. It maintains a global scan clock guarded by `clock_lock`; helper functions advance, reset, or read the starting offset depending on `scan_clock`.

`scan_thread` obtains the backend size, then loops from the current starting offset to the end in `scan_size` chunks. On each iteration it drains queued commands under the control lock: `CMD_QUIT` exits, while `CMD_NOTIFY_PREAD` can jump the scan offset forward to a recently read position. It updates the global clock and issues `next->cache` for the current chunk, ignoring cache errors because scanning is advisory.

If `scan_forever` is enabled, the thread resets the clock and starts over after reaching the end; otherwise it logs completion and exits. The file depends on globals and command types declared in `scan.h`, which is outside this group.
