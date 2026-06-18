# File Research: sources/virtualization/libguestfs/daemon/cleanups.c

Small cleanup helper file for GCC cleanup attributes used in the daemon.

Key points:
- `cleanup_aug_close` closes non-null Augeas handles.
- `cleanup_free_stringsbuf` frees daemon `stringsbuf` instances.
- Supports macros declared in `daemon.h`: `CLEANUP_AUG_CLOSE` and `CLEANUP_FREE_STRINGSBUF`.
