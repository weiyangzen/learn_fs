<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-success-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_ptp-success-Xverbose.c

Purpose: verbose-xlat injected-success PTP variant. It defines `XLAT_VERBOSE 1` and includes `ioctl_ptp-success.c`.

Important APIs/types/functions: Inherits all base PTP helpers and `INJECT_RETVAL 42`; local effect is verbose xlat rendering.

Control flow: injection setup locks onto `PTP_CLOCK_GETCAPS`, then the full PTP matrix runs with read buffers decoded as successes and verbose command/flag xlat strings.

State and persistence behavior: local PTP structs only; no real device state.

Dependencies/integration points: combines strace injection, PTP decoder coverage, and verbose xlat formatting.

Risks and test signals: sensitive to xlat table wording and header values. Passing output confirms verbose PTP success-path decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-success-Xverbose.c -->
