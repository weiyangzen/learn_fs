<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_get_info.c -->
# sources/test-tools/strace/tests/ioctl_pidfd_get_info.c

Purpose: tests decoding of the `PIDFD_GET_INFO` ioctl, including real pidfd calls and an extensive injected-success matrix for all known masks and struct-size versions.

Important APIs/types/functions: Uses `syscall(__NR_pidfd_open)`, `ioctl`, `struct pidfd_info`, `linux/pidfd.h`, `PIDFD_INFO_*`, `PIDFD_COREDUMP_*`, `PIDFD_GET_INFO`, undersize/oversize `_IOC` command encodings, `do_ioctl_fd`, `print_pidfd_info`, `skip_ioctls`, and `injected_pidfd_get_info_decode_checks`.

Control flow: non-injected mode opens a pidfd for self, checks invalid fd, EFAULT pointer, undersized command, oversized command, and normal command with `PIDFD_INFO_PID`, printing returned masks and optional creds/cgroup fields. Injected mode optionally exits when no args are supplied, otherwise locks onto injected return and runs crafted cases for unknown/all masks, pid, creds, cgroupid, supported mask, exit status decoding, coredump masks, coredump signal/code, all-known combined mask, and version 0/1/2 command sizes.

State and persistence behavior: non-injected mode creates a transient pidfd for the current process; injected mode mutates only local `pidfd_info`. No persistent state.

Dependencies/integration points: depends on recent pidfd UAPI, syscall-number support, signal/status decoding, xlat modes, and syscall injection.

Risks and test signals: kernel support may be absent or return different supported masks; injected path protects decoder coverage from kernel variability. Passing output confirms pidfd info command sizing, mask-driven field selection, exit/coredump formatting, and xlat mode compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_get_info.c -->
