# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/dev.c

Common Plan 9 device helper implementation for drawterm.

Key responsibilities:
- Provides Qid creation, device lookup by device character, directory entry construction, and generic directory generation.
- Implements generic attach, clone, walk, stat, directory read, permission check, open, create-denied, block read/write wrappers, remove-denied, wstat-denied, power-denied, and config-denied helpers.
- Documents expectations and contradictions around `Devgen` behavior for children versus siblings.

Important behavior:
- `devwalk()` clones channels, processes `.`/`..`, and handles partial walk results like Plan 9.
- `devstat()` synthesizes directory stat data if a directory generator cannot find the current directory by sibling enumeration.
- `devopen()` checks permission then marks the channel open and sets mode.
- `devbread()` and `devbwrite()` adapt byte-buffer device methods to `Block`-oriented callers.

Dependencies:
- Depends on `devtab`, `Chan`, `Dirtab`, `Dir`, 9P stat conversion, process user state, and Plan 9 error handling.

Notable risks:
- Generic helpers assume device generators honor enough of the documented contract; broken `Devgen` implementations can break walk/stat/read behavior.
