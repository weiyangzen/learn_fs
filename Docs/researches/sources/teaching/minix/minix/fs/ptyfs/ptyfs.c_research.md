# File Research: sources/teaching/minix/minix/fs/ptyfs/ptyfs.c

PTYFS is the `/dev/pts` filesystem server for Unix98 pseudoterminal slave nodes. It is an `fsdriver`-based in-memory filesystem whose root inode is fixed at `ROOT_INO_NR` and whose slave inodes are computed as `BASE_INO_NR + index`.

Key responsibilities:
- Mounts as a non-root filesystem and returns a synthetic root node.
- Resolves `"."` and numeric slave names through `ptyfs_lookup`.
- Enumerates `"."`, `".."`, and allocated slave nodes through `ptyfs_getdents`.
- Supports metadata-only `chown`, `chmod`, `stat`, and `statvfs`.
- Accepts non-filesystem messages only from the service label `"pty"`:
  - `PTYFS_SET` creates/updates a slave node entry.
  - `PTYFS_CLEAR` removes a slave node entry.
  - `PTYFS_NAME` returns the generated slave node name.
- Initializes node storage through `init_nodes()` and exits cleanly on `SIGTERM`.

Important interactions:
- Depends on `node.h` functions `init_nodes`, `get_node`, `set_node`, `clear_node`, and `get_max_node`.
- Uses DS label lookup to restrict control messages to the PTY service.
- Uses `fsdriver_task` with a small callback table.

Notable implementation detail:
- `parse_name` rejects non-digits, leading zeroes, and arithmetic overflow.
- `make_name` calls `snprintf(name, sizeof(name), ...)` even though `name` is a pointer parameter; this limits writes to pointer-size bytes rather than the supplied `size`, which can truncate large slave names while still returning success if `r < size`.
