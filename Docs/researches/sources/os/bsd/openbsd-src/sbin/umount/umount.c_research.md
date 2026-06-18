# File Research: sources/os/bsd/openbsd-src/sbin/umount/umount.c

Command-line filesystem unmount utility.

Options:
- `-a`: unmount all selected filesystems except root.
- `-f`: force unmount via `MNT_FORCE`.
- `-h host`: with `-a`, select NFS mounts matching host.
- `-t type`: include or exclude filesystem types; `no...` means exclusion list.
- `-v`: verbose output.

Mount resolution:
- Calls `sync()` at startup.
- For explicit targets, resolves DUIDs, real paths, devices, mount-on names, and mount-from names using `getmntinfo()`.
- `getmntname()` compares `f_mntfromname`, `f_mntfromspec`, and `f_mntonname`.
- `selected()` filters by typelist.
- `maketypelist()` mutates comma-separated type string into an argv-like array.

Unmount behavior:
- `umountall()` walks mount table in reverse and skips `/`.
- `umountfs()` validates directories/devices, resolves actual mountpoint, applies type/host filters, calls `unmount()`, and returns error status.
- For NFS, parses host/path from `host:path` or `path@host`, matches host aliases, and if not forced sends mountd `RPCMNT_UMOUNT` via UDP RPC after kernel unmount.
- `xdr_dir()` wraps `xdr_string()` for mount RPC.

Filesystem/storage relevance:
- Direct VFS administration tool. It exercises mount table inspection, filesystem type filtering, device/mountpoint resolution, forced unmount, and NFS server notification.
