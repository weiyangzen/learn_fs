<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_nbd.c -->
# sources/test-tools/strace/tests/ioctl_nbd.c

Purpose: tests Network Block Device ioctl command decoding, including command names, flag xlat values, scalar sizes/timeouts, and unknown command fallback.

Important APIs/types/functions: Uses `linux/nbd.h`, `xlat/nbd_ioctl_cmds.h`, `xlat/nbd_ioctl_flags.h`, `ioctl`, `open`, and NBD constants including `NBD_SET_SOCK`, `NBD_SET_BLKSIZE`, `NBD_SET_SIZE`, `NBD_DO_IT`, `NBD_CLEAR_SOCK`, `NBD_CLEAR_QUE`, `NBD_PRINT_DEBUG`, `NBD_SET_SIZE_BLOCKS`, `NBD_DISCONNECT`, `NBD_SET_TIMEOUT`, `NBD_SET_FLAGS`, `NBD_SET_TAG`, and `NBD_SET_DESCRIPTION`.

Control flow: opens `/dev/null` or uses invalid fds to produce stable EBADF/EINVAL-style output, calls each NBD command with representative integer, pointer, and string arguments, prints flag combinations, and emits unknown `_IO` command text.

State and persistence behavior: no NBD device state is persisted; invalid or harmless fds make this a decoder-only test.

Dependencies/integration points: integrates NBD UAPI command and flag xlat tables with strace ioctl decoding.

Risks and test signals: aliases and kernel header changes can alter names. Passing output confirms command recognition, scalar/string argument formatting, and unknown NBD ioctl fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_nbd.c -->
