# File Research: sources/os/bsd/freebsd-src/sbin/fsck/fsutil.c

Utility functions shared by generic `fsck` and related fsck code.

Key responsibilities:
- `getfsopt()` tests whether an fstab mount option or its `no...` inverse is present.
- `setcdevname()` and `cdevname()` maintain current device name and preen mode.
- `pfatal()`, `pwarn()`, `perr()`, and `panic()` provide fsck-style message handling.
- `devcheck()` validates that a path exists and is a character device.
- `emalloc()`, `erealloc()`, and `estrdup()` are checked allocation wrappers.

Important behavior:
- In preen mode, fatal messages include the device name and print “UNEXPECTED INCONSISTENCY; RUN <prog> MANUALLY.” before exiting with status 8.
- `getfsopt()` handles six positive/negative mount option cases, treating `foo` and `nofoo` distinctly.
- `devcheck()` currently stats `/` and the supplied device and emits errors through `perr()`.

Risks and constraints:
- `getfsopt()` assumes `strdup()` succeeds; unlike allocation wrappers, it does not check for NULL.
- `devcheck()` returns the original name even after reporting problems, so callers must rely on fatal behavior or later errors.
