# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_note.c

This file implements `/proc/<pid>/note` write parsing. `procfs_donote()` rejects reads, copies a bounded note string from user space using `vfs_getuserstr()`, and currently returns `EOPNOTSUPP`.

Research notes: the “send to process notify function” behavior is stubbed out, so note writes are parsed but unsupported.
