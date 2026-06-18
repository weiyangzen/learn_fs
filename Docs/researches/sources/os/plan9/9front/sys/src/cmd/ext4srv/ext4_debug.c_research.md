# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_debug.c

Minimal debug mask storage for ext4srv.

Key behavior:
- Maintains a static `debug_mask`.
- `ext4_dmask_set` ORs bits into the mask.
- `ext4_dmask_clr` clears bits.
- `ext4_dmask_get` returns the current mask.

Notable dependencies:
- Debug printing macros in headers use this mask to decide which subsystem messages to emit.

Research notes:
- There is no locking around the debug mask; it is process-global mutable state.
