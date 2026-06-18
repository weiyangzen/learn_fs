<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_get_info-success-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_pidfd_get_info-success-Xraw.c

Purpose: raw-xlat injected-success variant for `PIDFD_GET_INFO`. It defines `XLAT_RAW 1` and includes the success wrapper.

Important APIs/types/functions: Inherits all `PIDFD_GET_INFO` injected decode scenarios from `ioctl_pidfd_get_info.c`; local effect is raw numeric xlat rendering.

Control flow: after injection lock, all crafted `pidfd_info` masks and versioned command sizes are printed with raw numeric values instead of symbolic-first names.

State and persistence behavior: local buffer and injected return state only.

Dependencies/integration points: validates strace `-X raw` behavior for pidfd info commands and masks.

Risks and test signals: exact numeric command encodings and mask values are the signal. Passing output confirms raw xlat mode does not lose field decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_get_info-success-Xraw.c -->
