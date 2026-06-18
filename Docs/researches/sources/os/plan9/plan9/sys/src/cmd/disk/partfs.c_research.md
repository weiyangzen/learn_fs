# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/partfs.c

This file implements a userspace 9P server exposing partitions over an underlying disk image or sd-style directory.

Key behavior:
- Maintains up to 64 `Part` records with name, mode, version, sector offset, and sector length.
- Exposes a root containing one device directory named by `sdname`; inside are `ctl` and partition files.
- `ctlstring` reports inquiry, geometry, and partition lines.
- `ctlwrite` supports `part`, `delpart`, `inquiry`, and `geometry`; unknown control messages pass through to an underlying ctl fd if present.
- `addpart` and `delpart` manage partition table state and qid versions.
- `rdwrpart` bounds-checks reads/writes and maps partition-relative byte offsets to the underlying file.
- Implements lib9p handlers: attach, walk1, open, read, write, stat.
- `addparts` imports boot-style partition specs like `name start end/name start end`.
- `main` opens a file or sd directory, creates a default `data` partition, optionally imports `-p` parts, and posts/mounts the server.

Options:
- `-D`: chatty 9P.
- `-d sdname`: device directory name.
- `-m mtpt`: mount point, default `/dev`.
- `-p 9parts`: initial partition string.
- `-r`: read-only open of backing file.
- `-s srvname`: post service name.

Notable detail:
- `rdonly` changes how the backing file is opened, but partition file modes are still initialized from `ctlmode`; write attempts fail at underlying fd/write behavior.
