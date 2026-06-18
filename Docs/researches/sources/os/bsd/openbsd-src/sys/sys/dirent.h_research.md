# File Research: sources/os/bsd/openbsd-src/sys/sys/dirent.h

This header defines the directory entry ABI returned by `getdents(2)`.

Key definitions:
- `struct dirent` with file number, post-entry offset, record length, file type, name length, padding, and NUL-terminated name.
- `MAXNAMLEN` under `__BSD_VISIBLE`.
- File type constants: `DT_UNKNOWN`, `DT_FIFO`, `DT_CHR`, `DT_DIR`, `DT_BLK`, `DT_REG`, `DT_LNK`, `DT_SOCK`.
- Conversion macros: `IFTODT`, `DTTOIF`.
- Kernel record-size macros: `DIRENT_RECSIZE(namelen)` and `DIRENT_SIZE(dp)`.

Behavior and integration:
- Includes `<sys/cdefs.h>` for feature visibility.
- Directory entries are padded for alignment and names are guaranteed NUL-terminated.

Risk notes:
- The structure is syscall ABI; field size or alignment changes would break userland.
- `DIRENT_RECSIZE` includes the terminating NUL and rounds to 8-byte alignment.
