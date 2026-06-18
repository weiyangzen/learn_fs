# File Research: sources/os/bsd/netbsd-src/lib/libukfs/ukfs.h

Public API header for `libukfs`.

Key contents:
- Declares opaque types:
  - `struct ukfs`
  - `struct ukfs_dircookie`
  - `struct ukfs_part`
- Defines:
  - default mount path `UKFS_DEFAULTMP`
  - release flags
  - ABI version and `ukfs_init()` wrapper.
- Declares mount/release APIs:
  - `ukfs_mount`
  - `ukfs_mount_disk`
  - `ukfs_release`
- Declares POSIX-like filesystem operation wrappers.
- Declares accessors:
  - `ukfs_getmp`
  - `ukfs_getrvp`
  - `ukfs_setspecific`
  - `ukfs_getspecific`
- Declares partition probe/release/string APIs.
- Defines device path magic strings for disklabel and offset selection.
- Declares dynamic module loading:
  - `ukfs_modload`
  - `ukfs_modload_dir`
  - `ukfs_vfstypes`
- Declares `ukfs_util_builddirs`.

Role in subsystem:
- Public contract for programs accessing filesystem images through rump `libukfs`.
