<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/k_sockopt.c -->
# sources/test-tools/strace/tests/k_sockopt.c

Purpose: Tests raw kernel socket option syscall entry points by invoking architecture-specific syscall numbers for `getsockopt` and `setsockopt`.

Important APIs/types/functions: Uses `syscall`, `__NR_socketcall`-style numbering abstractions from `scno.h`, constants `SC_getsockopt` and `SC_setsockopt`, `fill`/`bad` kernel_ulong fixtures, and shared declarations from `k_sockopt.h`.

Control flow: Builds deliberately malformed scalar and pointer arguments, invokes the raw get/set sockopt syscall forms, and prints expected formatting for level, optname, optval, optlen, and return code.

State/persistence behavior: No real socket state is created; bogus descriptors and pointers drive failure-path decoding.

Dependencies: Depends on kernel syscall ABI availability for direct socket options and the companion header for function prototypes/macros.

Integration points: Covers lower-level socket option syscall decoding separate from libc `getsockopt`/`setsockopt` wrappers.

Risks: Socketcall multiplexing differs by architecture, and direct syscall numbers may be unavailable on some targets.

Test signals: Expected output is a compact set of failed raw sockopt syscall lines.

Source read signal: complete file read for this research pass; file size 61 line(s), 1407 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/k_sockopt.c -->
