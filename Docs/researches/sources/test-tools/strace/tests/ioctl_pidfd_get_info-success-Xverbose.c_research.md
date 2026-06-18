<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_get_info-success-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_pidfd_get_info-success-Xverbose.c

Purpose: verbose-xlat injected-success variant for `PIDFD_GET_INFO`. It defines `XLAT_VERBOSE 1` and includes the success wrapper.

Important APIs/types/functions: Inherits `PIDFD_GET_INFO` command structs, masks, and injected `pidfd_info` scenarios from the base implementation.

Control flow: same injected success path as `ioctl_pidfd_get_info-success.c`, with verbose xlat formatting that includes symbolic names and numeric values for commands and masks.

State and persistence behavior: local buffer only; injection simulates successful kernel writes.

Dependencies/integration points: validates `-X verbose` output for pidfd info decoder fields.

Risks and test signals: sensitive to symbol names and numeric encodings. Passing output confirms verbose xlat mode for pidfd info and coredump masks.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_get_info-success-Xverbose.c -->
