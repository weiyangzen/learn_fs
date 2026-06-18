<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_ptp-Xverbose.c

Purpose: verbose-xlat variant for PTP ioctl decoding. It defines `XLAT_VERBOSE 1` before including `ioctl_ptp.c`.

Important APIs/types/functions: Inherits the base PTP test and uses verbose xlat formatting for commands, flags, clock ids, and enum values.

Control flow: same no-device PTP matrix as the base file, but expected output includes both numeric and symbolic information where xlat macros support it.

State and persistence behavior: local structs only; no PTP device is opened.

Dependencies/integration points: validates strace `-X verbose` output with PTP-specific decoders.

Risks and test signals: fragile to xlat naming changes. Passing output confirms verbose xlat formatting across the PTP command surface.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-Xverbose.c -->
