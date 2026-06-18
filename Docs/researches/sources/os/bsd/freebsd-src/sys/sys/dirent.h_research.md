# File Research: sources/os/bsd/freebsd-src/sys/sys/dirent.h

## Purpose
Defines the FreeBSD directory entry ABI returned by `getdirentries(2)` and helper sizing macros.

## Main Elements
- Declares `ino_t` and `off_t` if needed.
- `struct dirent` includes inode, next offset, record length, type, name length, explicit padding, and NUL-terminated `d_name`.
- `freebsd11_dirent` preserves the older ABI for compatibility/kernel use.
- Defines `DT_*` file type constants and `IFTODT`/`DTTOIF`.
- `_GENERIC_DIRLEN`, `_GENERIC_DIRSIZ`, min/max directory entry size macros.
- Kernel `dirent_terminate()` zeroes padding and NUL-terminates names.

## Dependencies And Integration
Consumed by filesystems, VFS directory reading, libc, and compatibility code.

## Risk Notes
Layout is ABI-critical. Comments explicitly note that `d_name` must remain last and padding is intentional to avoid LP64 ABI surprises.
