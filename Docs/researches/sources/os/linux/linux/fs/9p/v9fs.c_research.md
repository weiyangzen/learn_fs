# File Research: sources/os/linux/linux/fs/9p/v9fs.c

Implements 9p filesystem module setup, mount option parsing, session creation/destruction, and sysfs integration.

Key behavior:
- Defines the full `fs_parameter_spec` table for 9p core, client, fd transport, and RDMA transport options.
- Parses options including `debug`, `dfltuid`, `dfltgid`, `afid`, `uname`, `aname`, `nodevmap`, `noxattr`, `directio`, `ignoreqv`, `cache`, `cachetag`, `access`, `posixacl`, `locktimeout`, `msize`, `trans`, and protocol `version`.
- `get_cache_mode()` maps named cache modes: `none`, `readahead`, `mmap`, `loose`, and `fscache`.
- `v9fs_show_options()` emits active session options for mount display.
- `v9fs_session_init()`:
  - Creates the 9p client.
  - Sets protocol flags for legacy, 9P2000.u, or 9P2000.L.
  - Applies parsed options.
  - Computes `maxdata`.
  - Normalizes unsupported access/ACL combinations.
  - Attaches the initial root FID.
  - Optionally registers the FS-Cache session volume.
  - Adds the session to a global list.
- `v9fs_session_close()`, `v9fs_session_cancel()`, and `v9fs_session_begin_cancel()` close, disconnect, or begin disconnecting active sessions.
- Creates a `/sys/fs/9p` kobject and, when FS-Cache is enabled, exposes cache tags through a read-only `caches` attribute.
- Creates/destroys the `v9fs_inode_cache` slab.
- Module init registers the `9p` filesystem; exit unregisters it and cleans caches/sysfs.

Important interactions:
- Supplies shared option parsing to `vfs_super.c`.
- Session flags in `v9fs.h` are the central policy inputs for FID lookup, ACL support, xattrs, and caching.
