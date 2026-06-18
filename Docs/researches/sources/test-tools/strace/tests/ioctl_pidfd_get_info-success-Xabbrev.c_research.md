<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_get_info-success-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_pidfd_get_info-success-Xabbrev.c

Purpose: abbreviated-xlat injected-success variant for `PIDFD_GET_INFO`. It defines `XLAT_ABBREV 1` and includes the injected-success wrapper.

Important APIs/types/functions: Inherits `INJECT_RETVAL 42`, `struct pidfd_info`, mask constants, and injected decode checks from `ioctl_pidfd_get_info.c`.

Control flow: compilation applies abbreviated xlat formatting to the success path. Runtime locks onto injected `PIDFD_GET_INFO`, then prints crafted masks, pid/cred/cgroup/exit/coredump/support fields with abbreviated xlat strings.

State and persistence behavior: local `pidfd_info` buffer only; no real pidfd is required in the injected path.

Dependencies/integration points: combines strace injection and `-X abbrev` xlat output contracts.

Risks and test signals: fragile to xlat formatting changes. Passing output confirms abbreviated pidfd info masks and coredump masks under success decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_get_info-success-Xabbrev.c -->
