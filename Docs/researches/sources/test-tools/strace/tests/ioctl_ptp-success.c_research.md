<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-success.c -->
# sources/test-tools/strace/tests/ioctl_ptp-success.c

Purpose: syscall-injection success wrapper for PTP ioctl decoding. It defines `INJECT_RETVAL 42` and includes `ioctl_ptp.c`.

Important APIs/types/functions: Inherits `sys_ioctl`, `test_no_device`, and all PTP UAPI struct coverage from the base file.

Control flow: the included `main` requires a skip count, loops on `PTP_CLOCK_GETCAPS` until the injected return appears, then runs the base PTP no-device matrix with `errstr` annotated as injected and read-style structs printed as if successful.

State and persistence behavior: local test memory only; injection simulates device success.

Dependencies/integration points: validates strace syscall injection with PTP ioctl decoders.

Risks and test signals: injection setup must match expected retval. Passing output confirms success branches for caps, sys offsets, precise/extended timestamps, pin descriptors, and other PTP structs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-success.c -->
