# File Research: sources/os/bsd/netbsd-src/sys/sys/dirent.h

Defines NetBSD directory entry ABI and directory record helper macros.

Key content:
- `struct dirent`: inode number, record length, name length, file type, fixed maximum name buffer.
- NetBSD-source `MAXNAMLEN` set to 511.
- File type constants: `DT_UNKNOWN`, `DT_FIFO`, `DT_CHR`, `DT_DIR`, `DT_BLK`, `DT_REG`, `DT_LNK`, `DT_SOCK`, `DT_WHT`.
- Alignment and record macros: `_DIRENT_ALIGN`, `_DIRENT_NAMEOFF`, `_DIRENT_RECLEN`, `_DIRENT_SIZE`, `_DIRENT_NEXT`, `_DIRENT_MINSIZE`.
- Mode conversion: `IFTODT`, `DTTOIF`.

Important behavior:
- Comments warn macros are used both with exposed `struct dirent` and UFS/FFS `struct direct`, so they remain type-polymorphic.
- Modern `struct dirent` uses 8-byte alignment via inode field size.
