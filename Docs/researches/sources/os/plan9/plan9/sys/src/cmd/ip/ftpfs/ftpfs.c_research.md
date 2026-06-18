# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ftpfs/ftpfs.c

`ftpfs.c` exposes a remote FTP server as a local 9P filesystem.

Key behavior:
- Parses options for mount root, password, mount point, NLST mode, extension suffix, TLS flag, OS type override, root path, quiet mode, key spec, and keepalive.
- Connects/logs into FTP server via protocol functions, builds remote tree, then forks a 9P server and mounts it.
- Maintains active fids mapped to `Node` path tree entries.
- Implements 9P handlers for version, attach, walk, open, create, read, write, clunk, remove, stat, and wstat/auth stubs.
- `rwalk` traverses cached/remote paths, supports `.flush.ftpfs`, handles TOPS/VM/VMS top-level quirks, and probes unknown paths by attempting `changedir`.
- `ropen` caches directories with `readdir` and files with `readfile`; `rcreate` creates dirs remotely or marks files dirty.
- `rread` serializes directory entries or reads cached file content.
- `rwrite` writes to local cache and marks dirty.
- `rclunk` writes dirty files back via `createfile`.
- Tree helpers manage `Node` creation, path extension, cache invalidation, special top-level directories, and symlink type fixing.

Important dependencies:
- Uses FTP protocol functions declared in `ftpfs.h` and caching functions from `file.c`.

Notable risks/quirks:
- `-t` sets `usetls`, but TLS behavior depends on protocol-side implementation not in this file.
- `rwstat` and `rauth` are unimplemented.
