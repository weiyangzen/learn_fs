<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/iopl.c -->
# sources/test-tools/strace/tests/iopl.c

Purpose: Tests strace decoding of the `iopl` syscall on architectures exposing `__NR_iopl`.

Important APIs/types/functions: Uses `syscall(__NR_iopl, level)`, `kernel_ulong_t`, `sprintrc`, and `SKIP_MAIN_UNDEFINED`.

Control flow: Performs a single bogus `iopl` call with a wide constant, prints the truncated level as strace should see it, and exits.

State/persistence behavior: The invalid privilege-level request should fail; no persistent process I/O privilege state is expected.

Dependencies: Architecture syscall availability and normal kernel privilege enforcement.

Integration points: Covers scalar argument formatting for legacy x86-style I/O privilege syscalls.

Risks: Privilege-sensitive syscalls must not accidentally succeed in a way that changes the test process state; the bogus value mitigates that.

Test signals: One decoded `iopl(...)` line or skip on unsupported targets.

Source read signal: complete file read for this research pass; file size 30 line(s), 415 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/iopl.c -->
