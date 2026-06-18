# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_main.c

This file is the FreeBSD FUSE module entry point. It registers the `fusefs` VFS type, exposes sysctl nodes, initializes/destroys subsystem state, and handles module load/unload.

Key responsibilities:
- Defines global `struct mtx fuse_mtx`, used as the broad FUSE global lock.
- Declares external subsystem objects:
  - `fuse_vfsops`
  - `fuse_cdevsw`
  - `fuse_fifonops`
- Defines `fuse_vfsconf`:
  - name `fusefs`
  - VFS ops pointer
  - dynamic type number
  - flags `VFCF_JAIL | VFCF_SYNTHETIC`
- Creates sysctl nodes:
  - `vfs.fusefs`
  - `vfs.fusefs.stats`
  - read-only kernel ABI major/minor sysctls.
- Defines SDT provider `fusefs`.
- Implements `fuse_bringdown`.
  - Destroys node, internal, file, IPC, and device subsystems.
  - Destroys `fuse_mtx`.
- Implements `fuse_loader`.
  - On `MOD_LOAD`:
    - initializes `fuse_mtx`;
    - initializes device, IPC, file, internal, and node subsystems;
    - registers the VFS with `vfs_modevent`.
    - rolls back through `fuse_bringdown` if VFS registration fails.
  - On `MOD_UNLOAD`:
    - unregisters VFS through `vfs_modevent`;
    - runs `fuse_bringdown`.
  - Rejects other events with `EINVAL`.
- Registers module metadata with `DECLARE_MODULE(fusefs, ...)` and `MODULE_VERSION(fusefs, 1)`.

Integration points:
- Owns startup/shutdown ordering for:
  - `/dev/fuse` device code
  - IPC tickets
  - file handles
  - shared internal counters
  - vnode counters/state
  - VFS registration
- Sysctl nodes are extended by other files in this group.

Notable risks and research hooks:
- Bringdown ordering assumes no active mounts after VFS unregister succeeds.
- The `eventhandler_tag` parameter to `fuse_bringdown` is currently unused.
- Failed `fuse_device_init` only destroys `fuse_mtx`; later failures use full bringdown.
