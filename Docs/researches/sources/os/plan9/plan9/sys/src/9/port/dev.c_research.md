# File Research: sources/os/plan9/plan9/sys/src/9/port/dev.c

This file provides generic helpers for Plan 9 kernel device implementations.

Key responsibilities:
- Creates qids via `mkqid` and resolves device letters via `devno`.
- Builds `Dir` records with `devdir`.
- Provides default no-op reset/init/shutdown hooks.
- Implements generic attach and clone behavior for synthetic devices.
- Implements `devgen`, `devwalk`, `devstat`, and `devdirread` for table- or generator-backed directory trees.
- Implements permission checking and `devopen`.
- Provides default failing create/remove/wstat/power/config operations.
- Provides `devbread` and `devbwrite` wrappers converting read/write calls to `Block` operations.

Important implementation details:
- Comments document the subtle expectations around `Devgen` behavior for children versus siblings.
- `devwalk` handles `.` and `..`, partial walks, and cloned channels.
- Directory opens are read-only.

Filesystem/storage relevance:
- This is shared scaffolding for synthetic filesystem-like devices in Plan 9.
- Storage drivers such as AoE and BIOS/audio devices use this pattern to expose control/data files under the namespace.
