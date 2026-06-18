# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/flash.c

This file is the main executable for mounting a journaled flashfs instance.

Key behavior:
- Parses options for read-only mode, sector count, sector size, mount point, backing file/device, and 9P debug.
- Initializes the storage backend, sector buffer, entry tree, and journal state.
- Loads the filesystem from flash sectors.
- Serves the mounted namespace.

Important details:
- Defaults to backing device `/dev/flash/fs` and mount point `/n/brzr`.
- Uses `loadfs(ro)` before serving.
- Requires storage geometry from arguments or the backend.

Filesystem relevance:
- Direct: flashfs server entry point.
