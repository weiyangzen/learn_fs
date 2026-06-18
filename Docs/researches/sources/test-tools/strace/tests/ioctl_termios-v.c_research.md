<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_termios-v.c -->
# sources/test-tools/strace/tests/ioctl_termios-v.c

Purpose: verbose variant of the termios ioctl decoder test. It defines `VERBOSE 1` and includes `ioctl_termios.c`.

Important APIs/types/functions: Inherits the base termios ioctl matrix and termios/termios2/winsize/serial-related structures from `ioctl_termios.c`; local behavior is compile-time verbose formatting.

Control flow: runtime follows the base termios test but takes verbose branches for structure fields and flag sets, producing expanded expected output for terminal attributes and related ioctls.

State and persistence behavior: local test buffers and invalid fds dominate; verbose mode changes only printed expectations.

Dependencies/integration points: integrates strace verbose output mode with terminal ioctl decoders and platform termios headers.

Risks and test signals: depends on the included base file outside this group and platform-specific termios definitions. Passing output confirms verbose terminal ioctl structure rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_termios-v.c -->
