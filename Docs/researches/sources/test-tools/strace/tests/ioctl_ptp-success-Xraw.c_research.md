<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-success-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_ptp-success-Xraw.c

Purpose: raw-xlat injected-success PTP variant. It defines `XLAT_RAW 1` and includes the success wrapper.

Important APIs/types/functions: Inherits PTP structures, command matrix, and `INJECT_RETVAL 42` behavior from `ioctl_ptp.c` via `ioctl_ptp-success.c`.

Control flow: after injection lock, every PTP read/write scenario prints raw numeric xlat values while still showing successful output-buffer decoding.

State and persistence behavior: local test buffers only; injection simulates kernel success.

Dependencies/integration points: validates raw xlat mode with PTP success-path decoding.

Risks and test signals: numeric command encodings and struct layouts are the expected-output contract. Passing output confirms raw mode plus injected reads remain coherent.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-success-Xraw.c -->
