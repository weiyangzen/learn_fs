<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_get_info-success.c -->
# sources/test-tools/strace/tests/ioctl_pidfd_get_info-success.c

Purpose: injected-success wrapper for `PIDFD_GET_INFO`. It defines `INJECT_RETVAL 42` and includes the base pidfd info test.

Important APIs/types/functions: Inherits `do_ioctl_fd`, `skip_ioctls`, `injected_pidfd_get_info_decode_checks`, `struct pidfd_info`, mask constants, and versioned command encodings from `ioctl_pidfd_get_info.c`.

Control flow: with injection arguments, the included `main` skips until `PIDFD_GET_INFO` returns the injected value, then runs the synthetic decoder matrix for masks, versioned struct sizes, pid/creds/cgroup/exit/coredump/signal/code/support fields.

State and persistence behavior: no real pidfd is needed; all output data is explicitly written into a local `pidfd_info` buffer.

Dependencies/integration points: exercises strace syscall injection and pidfd info UAPI xlat tables.

Risks and test signals: requires correct injection setup. Passing output confirms success-path parsing of every known `pidfd_info` field and legacy struct-size variants.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_get_info-success.c -->
