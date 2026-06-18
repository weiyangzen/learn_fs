# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/dev.c

Generic Plan 9 device helper routines for the VNC user-space device filesystem.

Key responsibilities:
- Creates `Qid` values and locates device table entries by device character.
- Fills `Dir` structures from `Dirtab` data.
- Implements generic attach, clone, walk, stat, directory read, permission check, and open operations.
- Provides default deny/panic implementations for create, block I/O, remove, and wstat.

Important behavior:
- `devgen()` expects table entry zero to be the directory itself.
- `devwalk()` supports cloning, partial walks, `.`, `..`, and generator-driven lookup.
- `devstat()` synthesizes a directory stat if no table entry matches a directory channel.
- `devopen()` rejects non-read opens on directories and sets `COPEN`.

Risks:
- Permission checks are simplified to owner/eve/other mapping.
- Directory read has a comment questioning offset handling for skipped entries.
