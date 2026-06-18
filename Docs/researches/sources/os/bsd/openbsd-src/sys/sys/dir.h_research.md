# File Research: sources/os/bsd/openbsd-src/sys/sys/dir.h

This compatibility header maps old BSD `struct direct` usage to modern `struct dirent`.

Key definitions:
- Includes `<dirent.h>`.
- Defines `direct` as `dirent`.
- Defines legacy `DIRSIZ(dp)` record-size calculation using `d_namlen`.

Behavior and integration:
- Explicitly rejects kernel use with `#error "Please use <sys/dirent.h> instead"`.
- Exists only for old user-level compatibility.

Risk notes:
- `DIRSIZ` uses legacy 4-byte rounding, while kernel `DIRENT_RECSIZE` in `dirent.h` uses 8-byte alignment.
