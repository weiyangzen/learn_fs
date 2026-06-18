<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mknod.c -->
# sources/test-tools/strace/src/mknod.c

Purpose: decodes `mknod` and `mknodat` path, mode, and device arguments.
Important APIs/types/functions: `decode_mknod`, `SYS_FUNC(mknod)`, `SYS_FUNC(mknodat)`, `printpath`, `print_dirfd`, `print_symbolic_mode_t`, and `print_dev_t`.
Control flow: prints path arguments first, then mode; device number is decoded only for character/block/fifo/socket cases where meaningful. State and persistence behavior: none.
Dependencies and integration points: filesystem syscall decoders. Risks: mode-type switch determines whether `dev` is printed symbolically or raw. Test signals: regular, char/block, fifo, socket, mknodat dirfd, and unusual mode tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mknod.c -->
