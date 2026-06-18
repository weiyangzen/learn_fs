# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9fs_proto.h

This small header defines p9fs-facing Plan 9 open mode constants:
- `P9FS_OREAD`
- `P9FS_OWRITE`
- `P9FS_ORDWR`
- `P9FS_OEXEC`
- `P9FS_OTRUNC`

Research-relevant notes:
- These are filesystem-layer constants, distinct from the fuller protocol enum in `p9_protocol.h`.
- The file currently contains only open permission bits and a commented-out include for virtio 9P definitions.
