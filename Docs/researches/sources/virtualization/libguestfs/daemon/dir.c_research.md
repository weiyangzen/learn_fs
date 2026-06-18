# File Research: sources/virtualization/libguestfs/daemon/dir.c

Implements directory creation/removal APIs.

Key points:
- `do_rmdir`, `do_mkdir`, and `do_mkdir_mode` call libc operations inside sysroot chroot.
- `do_rm_rf` blocks removing `/`, then runs `rm -rf` on the sysroot path.
- `do_mkdir_mode` rejects negative modes.
- `recursive_mkdir` implements mkdir-p semantics and distinguishes existing non-directory path components.
- `do_mkdir_p` runs recursive creation inside chroot and maps `-2` to a clear “path element was not a directory” error.
