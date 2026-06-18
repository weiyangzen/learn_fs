# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/suspend.c

This file is a compatibility stub for puffs filesystem suspension. `puffs_fs_suspend` takes a `struct puffs_usermount *` but ignores it and returns `EOPNOTSUPP`.

The comment explains that suspension "used to be" implemented, but no longer is, and the function remains to avoid an ABI bump. Callers must therefore treat suspension as unsupported even though the symbol still exists in the library.
