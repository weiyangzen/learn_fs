<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_ptp-Xabbrev.c

Purpose: abbreviated-xlat variant for PTP ioctl decoding. It defines `XLAT_ABBREV 1` and includes the base PTP test.

Important APIs/types/functions: Inherits all PTP command coverage from `ioctl_ptp.c`; local behavior changes xlat rendering through `XLAT_ABBREV`.

Control flow: runtime is the base `test_no_device` matrix with abbreviated symbolic output for commands, flags, clock ids, and enum values.

State and persistence behavior: local PTP structs only; fd `-1` avoids device state.

Dependencies/integration points: validates strace abbreviated xlat mode for PTP decoders.

Risks and test signals: exact xlat format is the signal. Passing output confirms PTP fields remain decoded under abbreviated xlat settings.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-Xabbrev.c -->
