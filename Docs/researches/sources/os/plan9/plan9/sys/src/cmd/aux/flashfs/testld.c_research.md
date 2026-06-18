# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/testld.c

This file is a load/replay test utility for flashfs images.

Key behavior:
- Parses sector count, sector size, and file path.
- Validates minimum geometry.
- Initializes storage and entry tree.
- Calls `loadfs(1)` to load the filesystem read-only.

Important details:
- Program name is set to `testldfs`.
- Does not serve the filesystem; it tests loading and recovery.

Filesystem relevance:
- Direct test utility for flashfs journal loading.
