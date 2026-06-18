# File Research: sources/windows/dokany/dokan_fuse/include/fuse.h

Public high-level FUSE 2.x API compatibility header adapted for Windows.

Key contents:
- Includes `fuse_win.h` on Windows and defines `FUSE_OFF_T`/`FUSE_STAT` abstractions.
- Defaults `FUSE_USE_VERSION` to 27.
- Defines `fuse_fill_dir_t`, deprecated directory types, `fuse_operations`, and `fuse_context`.
- `fuse_operations` covers classic FUSE high-level callbacks:
  - metadata: `getattr`, `fgetattr`, `access`, `chmod`, `chown`, times;
  - namespace: `mknod`, `mkdir`, `unlink`, `rmdir`, `rename`, links;
  - file I/O: `open`, `read`, `write`, `flush`, `release`, `fsync`;
  - directory I/O: `opendir`, `readdir`, `releasedir`, `fsyncdir`;
  - xattrs, `statfs`, locking, `bmap`, init/destroy.
- Adds Windows-specific extension callbacks:
  - `win_get_attributes`
  - `win_set_attributes`
  - `win_set_times`
- Declares main/setup/loop API: `fuse_main`, `fuse_new`, `fuse_loop`, `fuse_loop_mt`, `fuse_exit`, `fuse_setup`, `fuse_teardown`.
- Declares stacking/module APIs and per-operation `fuse_fs_*` wrappers.
- Includes compatibility macro remapping for older FUSE API versions.

Role:
- Allows FUSE-style filesystem programs to compile against Dokan’s Windows adapter.
