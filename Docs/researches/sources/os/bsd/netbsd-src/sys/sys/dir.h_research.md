# File Research: sources/os/bsd/netbsd-src/sys/sys/dir.h

Backward-compatibility header mapping old BSD `struct direct` usage to modern `struct dirent`.

Key content:
- Rejects kernel use with `#error "Please use <sys/dirent.h> instead"`.
- Includes `<dirent.h>`.
- Defines `direct` as `dirent`.
- Defines compatibility `DIRSIZ(dp)` record length macro.

Important behavior:
- Exists for old user-level source compatibility only.
- `DIRSIZ` computes minimum record length rounded to a 4-byte boundary.
