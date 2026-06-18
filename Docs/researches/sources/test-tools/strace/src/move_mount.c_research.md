<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/move_mount.c -->
# sources/test-tools/strace/src/move_mount.c

Purpose: decodes `move_mount` source and target path/fd pairs plus flags.
Important APIs/types/functions: `SYS_FUNC(move_mount)`, `print_dirfd`, `printpath`, and `move_mount_flags`.
Control flow: prints from dirfd/path, to dirfd/path, then symbolic flags. State and persistence behavior: none.
Dependencies and integration points: mount API syscall table. Risks: dirfd/path ordering must match kernel ABI. Test signals: file-descriptor paths, `AT_FDCWD`, empty paths, and flag combinations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/move_mount.c -->
