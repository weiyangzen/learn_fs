# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/dummy.c

This file starts an in-memory/dummy flashfs service.

Key behavior:
- Sets program name to `dummyfs`.
- Defaults mount path to `/n/brzr`.
- Sets `limit` to 100 KiB.
- Initializes the entry tree and serves the filesystem.

Important details:
- Supports `-m` to choose the mount point.
- Does not load a backing flash journal.

Filesystem relevance:
- Direct test harness for the flashfs namespace logic.
