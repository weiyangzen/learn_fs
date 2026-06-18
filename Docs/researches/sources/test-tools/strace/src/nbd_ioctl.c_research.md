<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/nbd_ioctl.c -->
# sources/test-tools/strace/src/nbd_ioctl.c

Purpose: decodes Network Block Device ioctls.
Important APIs/types/functions: `nbd_ioctl`, NBD ioctl constants, `nbd_ioctl_flags`, `printfd`, `PRINT_VAL_U`, and generic xlat command names.
Control flow: no-argument commands are marked decoded; `NBD_SET_SOCK` prints fd, size/block/time commands print unsigned values, and `NBD_SET_FLAGS` prints symbolic flags. Unknown codes fall back.
State and persistence behavior: stateless. Dependencies and integration points: ioctl dispatcher. Risks: some NBD arguments are scalar kernel_ulong_t values rather than pointers; treating them as pointers would be wrong. Test signals: each NBD_SET_* command, disconnect/no-arg commands, and unknown ioctl tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/nbd_ioctl.c -->
