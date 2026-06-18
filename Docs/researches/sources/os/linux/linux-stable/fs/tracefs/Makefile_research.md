# File Research: sources/os/linux/linux-stable/fs/tracefs/Makefile

Purpose: Builds tracefs when tracing is enabled.

Key responsibilities:
- Defines `tracefs-objs` as `inode.o` plus `event_inode.o`.
- Adds `tracefs.o` under `CONFIG_TRACING`.

Important interactions:
- Tracefs is tied to the tracing subsystem rather than being a standalone always-built filesystem.

Notable invariants and risks:
- Eventfs support is built into the same tracefs object.
