# File Research: sources/os/bsd/freebsd-src/sbin/fsck/fsutil.h

Header for generic fsck utility functions and option flags.

Declarations:
- `checkfstab()`
- `getfsopt()`
- `pfatal()`, `pwarn()`, `perr()`, `panic()`
- `devcheck()`
- `cdevname()`, `setcdevname()`
- `emalloc()`, `erealloc()`, `estrdup()`

Flags:
- `CHECK_PREEN`
- `CHECK_VERBOSE`
- `CHECK_DEBUG`
- `CHECK_BACKGRD`
- `DO_BACKGRD`
- `CHECK_CLEAN`

Role:
- Provides the shared API between `fsck.c`, `fsutil.c`, and `preen.c`.
