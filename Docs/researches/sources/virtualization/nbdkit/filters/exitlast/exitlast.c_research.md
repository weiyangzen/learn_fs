# File Research: sources/virtualization/nbdkit/filters/exitlast/exitlast.c

Purpose: shuts down nbdkit when the last active client connection closes.

Key details:
- Maintains an atomic unsigned connection count.
- `.open` delegates to backend and increments the count.
- `.close` decrements the count; when it reaches zero, logs and calls `nbdkit_shutdown`.
- No per-connection handle state is needed.

Risk notes:
- On platforms without `<stdatomic.h>`, the fallback treats plain 32-bit ints as sufficient for this simple counter.
