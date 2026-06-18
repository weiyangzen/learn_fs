<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-success-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_ptp-success-Xabbrev.c

Purpose: abbreviated-xlat injected-success PTP variant. It defines `XLAT_ABBREV 1` and includes `ioctl_ptp-success.c`.

Important APIs/types/functions: Inherits `INJECT_RETVAL 42` and all PTP test helpers from the base file.

Control flow: locks onto injected `PTP_CLOCK_GETCAPS`, then runs the PTP matrix with success-style read buffers and abbreviated xlat formatting.

State and persistence behavior: local PTP buffers only; injected return simulates successful reads.

Dependencies/integration points: combines syscall injection, PTP decoder coverage, and abbreviated xlat output.

Risks and test signals: requires injection arguments and stable xlat names. Passing output confirms abbreviated success-path PTP decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-success-Xabbrev.c -->
