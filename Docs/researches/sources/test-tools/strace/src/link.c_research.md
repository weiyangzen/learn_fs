# sources/test-tools/strace/src/link.c

Purpose: decodes hard-link, unlink-at, and symlink-at pathname syscalls.

Important APIs/types/functions: `SYS_FUNC(link)`, `SYS_FUNC(linkat)`, `SYS_FUNC(unlinkat)`, `SYS_FUNC(symlinkat)`, `printpath`, `print_dirfd`, `printflags`, and `at_flags`.

Control flow: each decoder prints named path and dirfd arguments in syscall order. `linkat` and `unlinkat` append `AT_*` flag decoding; `symlinkat` prints target, destination directory fd, and link path.

State and persistence behavior: no persistent state. Reads tracee strings through `printpath`.

Dependencies and integration points: depends on `<linux/fcntl.h>` for `AT_*` constants and the generated `at_flags` xlat table. Integrated with filesystem syscall decoders.

Risks: path memory can be inaccessible; dirfd semantics must preserve source vs destination naming. `at_flags` includes flags that are syscall-specific, so tests should allow unknown/future flags.

Test signals: cover absolute/relative paths, `AT_FDCWD`, nonstandard dirfds, `AT_SYMLINK_FOLLOW`, `AT_REMOVEDIR`, inaccessible paths, and unknown flag bits.
