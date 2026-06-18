<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_ptp-Xraw.c

Purpose: raw-xlat variant for PTP ioctl decoding. It defines `XLAT_RAW 1` before including the base test.

Important APIs/types/functions: Inherits PTP UAPI structs and command matrix from `ioctl_ptp.c`; raw mode changes command and flag formatting.

Control flow: base PTP no-device tests run with raw numeric xlat output, including unknown command sweeps and all major PTP struct families.

State and persistence behavior: no persistent state; local buffers and invalid fd only.

Dependencies/integration points: validates strace raw xlat behavior for PTP ioctl commands and flags.

Risks and test signals: command numeric encodings are sensitive to header definitions. Passing output confirms raw mode does not bypass struct decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-Xraw.c -->
