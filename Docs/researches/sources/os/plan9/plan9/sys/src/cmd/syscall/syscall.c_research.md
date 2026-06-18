# File Research: sources/os/plan9/plan9/sys/src/cmd/syscall/syscall.c

This file implements a command-line syscall exerciser.

Key behavior:
- Dispatches named syscalls from a generated `tab.h` table.
- Parses up to five arguments as integers, strings, or the special 1 MB `buf`.
- Special-cases `seek`, `pread`, and `pwrite` for vlong offsets.
- Prints return value and error state.
- Optional flags print buffer text (`-o`), hex/ascii dump (`-x`), or decode stat messages (`-s`).

Important details:
- Includes prototypes for syscalls not declared in libc.
- `-s` decodes Plan 9 stat buffers via `convM2D` and prints qid/mode/owner/time details.
- Notes are caught and reported before default handling.

Filesystem relevance:
- Direct diagnostic utility for filesystem syscalls such as `stat`, `wstat`, `read`, `write`, `mount`, `pread`, and `pwrite`.
