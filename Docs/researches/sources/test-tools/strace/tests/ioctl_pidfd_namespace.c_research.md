<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_namespace.c -->
# sources/test-tools/strace/tests/ioctl_pidfd_namespace.c

Purpose: tests `PIDFD_GET_*_NAMESPACE` ioctl command decoding for all namespace selectors exposed by `linux/pidfd.h`, plus an unknown pidfd ioctl fallback.

Important APIs/types/functions: Uses `ioctl`, `linux/pidfd.h`, `do_ioctl`, `sprintrc`, `struct strval32`, and command constants `PIDFD_GET_CGROUP_NAMESPACE`, `PIDFD_GET_IPC_NAMESPACE`, `PIDFD_GET_MNT_NAMESPACE`, `PIDFD_GET_NET_NAMESPACE`, `PIDFD_GET_PID_NAMESPACE`, `PIDFD_GET_PID_FOR_CHILDREN_NAMESPACE`, `PIDFD_GET_TIME_NAMESPACE`, `PIDFD_GET_TIME_FOR_CHILDREN_NAMESPACE`, `PIDFD_GET_USER_NAMESPACE`, `PIDFD_GET_UTS_NAMESPACE`, and `_IOC(_IOC_NONE, 0xff, 0xfe, 0xfd)`.

Control flow: builds a command table and an argument table containing `0` and `0xfacefeeddeadbeef`. For each command/argument pair it calls `ioctl(-1, cmd, arg)` and prints the command through `XLAT_SEL`, the raw argument as hex, and the `sprintrc` result. It ends with the standard strace test marker.

State and persistence behavior: no pidfd or namespace fd is opened; all calls use fd `-1`, so the test has no kernel namespace side effects. The only mutable state is the last `errstr`.

Dependencies/integration points: depends on pidfd namespace UAPI constants and strace xlat decoding for pidfd namespace command names.

Risks and test signals: header availability for newer namespace selectors can vary. Passing output confirms command-name recognition, raw argument formatting, and unknown pidfd ioctl fallback on EBADF paths.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_namespace.c -->
