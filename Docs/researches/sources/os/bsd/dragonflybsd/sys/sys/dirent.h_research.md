# File Research: sources/os/bsd/dragonflybsd/sys/sys/dirent.h

Directory entry ABI for `getdirentries(2)` and filesystem readdir output.

Key responsibilities:
- Defines `ino_t` as 64-bit if not already declared.
- Defines `struct dirent` with inode/file number, name length, file type, reserved padding, and fixed `d_name[256]`.
- Handles POSIX/BSD namespace compatibility: kernel or strict POSIX exposes `d_ino`; BSD-visible userland exposes `d_fileno` with `d_ino` macro alias.
- Defines BSD-visible `DT_*` file type constants, including whiteout and database record file.
- Defines `_DIRENT_MINSIZ`, `_DIRENT_RECLEN`, `_DIRENT_DIRSIZ`, and `_DIRENT_NEXT` helpers with 8-byte alignment.

Dependencies:
- Includes `sys/cdefs.h` and `machine/stdint.h`.

Notable risks:
- The fixed `d_name` is a compatibility choice; code must still allocate records based on computed record length.
- Readdir-producing filesystems must correctly set `d_namlen`, NUL termination, and alignment.
