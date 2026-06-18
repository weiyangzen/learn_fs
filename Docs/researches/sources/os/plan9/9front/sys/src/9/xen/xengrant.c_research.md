# File Research: sources/os/plan9/9front/sys/src/9/xen/xengrant.c

Purpose: 9front Xen kernel grant-table manager for sharing or transferring page frames with other domains.

Key behavior:
- `xengrantinit` sets up one grant-table frame via `GNTTABOP_setup_table`, maps it at `XENGRANTTAB`, and initializes a simple freelist of grant refs.
- `xengrant` allocates a ref, fills frame/domain, enforces ordering via `coherence()`, then publishes grant flags.
- `xengrantend` validates no active use or incomplete transfer, invalidates flags, frees the ref, and returns the frame.

Integration notes: Used by `xensystem.c` for `shareframe`, `donateframe`, and `acceptframe`.

Risk/attention points: `Nframes` is hardcoded to 1 and comments warn not to increase it without extra mappings. Exhaustion panics rather than returning an error.
