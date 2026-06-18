<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_tiocm.c -->
# sources/test-tools/strace/tests/ioctl_tiocm.c

Purpose: Tests decoding of modem-control TIOCM ioctls: `TIOCMGET`, `TIOCMBIS`, `TIOCMBIC`, and `TIOCMSET`.

Important APIs/types/functions: Uses `ioctl`, `sprintrc`, `kernel_ulong_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, and strace `XLAT_*` formatting macros for `TIOCM_*` flags. `do_ioctl` and `do_ioctl_ptr` centralize syscall execution and saved return formatting.

Control flow: For every command, the test issues NULL and faulting-pointer cases. For on-enter commands it passes invalid and valid modem flag words, expecting symbolic expansion such as `TIOCM_LE`, `TIOCM_DTR`, `TIOCM_RTS`, `TIOCM_CTS`, `TIOCM_CAR`, `TIOCM_DSR`, `TIOCM_OUT1`, `TIOCM_OUT2`, and `TIOCM_LOOP`; for the getter it expects only pointer printing on failure.

State/persistence behavior: All state is an in-memory `unsigned int` allocated at a guard page boundary. It uses fd `-1`, so no device state is mutated and all normal syscalls fail with EBADF.

Dependencies: Depends on tty ioctl constants from system headers and the strace test framework. MIPS has a different valid/invalid mask, handled by conditional `VALID_FLAGS` and `INVALID_FLAGS`.

Integration points: Exercises the ioctl decoder's distinction between input and output pointer semantics and its flag-table behavior under raw, abbreviated, and verbose xlat modes.

Risks: Architecture-specific modem-bit definitions can change output. Treating `TIOCMGET` as an on-enter argument would be a decoder bug because failed getters must not dereference the output buffer.

Test signals: Successful output prints NULL, fault address, unknown flag fallback, known flag expansion, `sprintrc` failures, and the final exit marker.

Source read signal: complete file read for this research pass; file size 104 line(s), 2377 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_tiocm.c -->
