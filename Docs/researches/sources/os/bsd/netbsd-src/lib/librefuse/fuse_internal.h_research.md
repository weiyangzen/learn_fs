# File Research: sources/os/bsd/netbsd-src/lib/librefuse/fuse_internal.h

This private ReFUSE header defines implementation-only structure and helper prototypes. It defines `_REFUSE_IMPLEMENTATION_` before including `fuse.h` so ReFUSE's own source files do not receive the public warning about missing `FUSE_USE_VERSION`.

The private `struct fuse` contains the underlying `struct puffs_usermount *`, a `dead` flag, and a pointer to the base `struct fuse_fs` layer. This confirms the high-level FUSE compatibility layer is backed by libpuffs.

`enum refuse_show_help_variant` defines internal help-output variants for full help and no-header help. Hidden declarations expose signal handler setup/removal, generic setup/teardown, generic `fuse_new`, mount/unmount/destroy, multithreaded loop, and command-line parsing. These symbols are hidden from users and are intended to be called by the versioned compatibility wrappers and implementation files.
