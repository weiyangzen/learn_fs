# File Research: sources/virtualization/libguestfs/lib/tmpdirs.c

Temporary, cache, socket, and PID path management.

Important behavior:
- All configured tmp/runtime/cache paths are converted to absolute paths and validated as directories.
- `guestfs_get_tmpdir` prefers API-set tmpdir, then environment tmpdir, then `/tmp`.
- `guestfs_get_cachedir` prefers API-set cachedir, then environment tmpdir, then `/var/tmp`.
- `guestfs_get_sockdir` uses `/tmp` for root so libvirt/qemu can reach sockets; non-root prefers runtime dir, then `/tmp`.
- Lazily creates per-handle tmpdir and sockdir as `libguestfsXXXXXX`.
- Root-created temporary directories are chmodded `0755` for qemu access.
- Generates unique temporary file paths, socket paths bounded by `UNIX_PATH_MAX`, and PID paths under sockdir.
- Creates and security-checks the cached supermin appliance directory `.guestfs-$uid`, requiring ownership by current UID, directory type, and no group/other write bits.
- Removes tmpdir/sockdir recursively through `rm -rf`.

Filesystem relevance:
- Supplies secure host-side scratch space for overlays, appliance caches, RPC serialization files, sockets, and temporary filesystem metadata outputs.
