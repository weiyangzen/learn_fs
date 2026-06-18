<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_termios.c -->
# sources/test-tools/strace/tests/ioctl_termios.c

Purpose: Exercises strace decoding of terminal termio, termios, and optional termios2 ioctl commands. It covers setters and getters for TCSETS*, TCGETS*, TCSETA*, TCGETA, TIOCSLCKTRMIOS, and TIOCGLCKTRMIOS, including command-name collisions on architectures where tty and sound ioctl numbers overlap.

Important APIs/types/functions: Uses `ioctl`, direct `openat` of `/dev/ptmx`, `struct termio`, `struct termios`, optional `struct termios2`, `kernel_ulong_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `fill_memory`, `fill_memory_ex`, `printxval`, and xlat tables `baud_options` and `term_line_discs`. Helper printers include `print_iflag`, `print_oflag`, `print_cflag`, `print_lflag`, `print_flags`, `print_termios_cc`, `print_termios2`, `print_termios`, `print_termio`, and `do_ioctl`.

Control flow: The program allocates tail-guarded structures, opens a real tty via `/dev/ptmx`, then iterates a table of command families. For each command it tests NULL, off-by-one, misaligned, and valid pointers. Setter commands populate the structure before the syscall so strace can print input data; getter commands issue the syscall first and print either decoded output or the raw pointer depending on return status. Setup variants intentionally use random fill, patterned fill, and deterministic flag/control-character values.

State/persistence behavior: It creates only process-local tty state through the opened ptmx descriptor and in-memory termios buffers. No persistent filesystem state is written. The expected output preserves errno across pre-syscall printing for getter cases, and the tty descriptor is needed to resolve ioctl collision names correctly.

Dependencies: Requires Linux tty/termios UAPI headers, syscall numbers from `scno.h`, strace test helpers, and architecture-specific macro availability such as `HAVE_STRUCT_TERMIOS2`, `HAVE_STRUCT_TERMIOS_C_ISPEED`, `IBSHIFT`, `CIBAUD`, and layout differences for Alpha, PowerPC, MIPS, SPARC, HPPA, and others.

Integration points: Validates strace's ioctl decoder, xlat rendering, structure field printers, verbose versus abbreviated control-character output, and architecture-specific tty ABI handling. It is also a regression test for ioctl number ambiguity when an invalid fd prevents type-based disambiguation.

Risks: Output is highly architecture-sensitive: control-character indexes, unknown flag masks, `XTABS` handling, input/output speed fields, and clashed ioctl names differ by platform. A kernel or libc header change can alter field availability or constants. The test also depends on `/dev/ptmx` being available.

Test signals: Expected output includes decoded bitsets for input/output/control/local flags, c_cc arrays in verbose builds, line disciplines, `sprintrc` return strings, invalid pointer fallbacks, and `+++ exited with 0 +++`. Failures usually indicate a tty ioctl decoder regression, bad arch conditional, or changed UAPI layout.

Source read signal: complete file read for this research pass; file size 1003 line(s), 22385 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_termios.c -->
