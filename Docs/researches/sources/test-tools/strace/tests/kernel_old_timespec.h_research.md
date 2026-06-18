<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kernel_old_timespec.h -->
# sources/test-tools/strace/tests/kernel_old_timespec.h

Purpose: Compatibility header defining the old Linux kernel `timespec` layout used by strace tests that need pre-time64 ABI structures.

Important APIs/types/functions: Provides a small kernel-facing structure definition with old-width seconds/nanoseconds fields. It is a header-only artifact and exports no functions.

Control flow: There is no runtime control flow. Including C tests use the type at compile time to build syscall or ioctl argument fixtures.

State/persistence behavior: No state is stored. The header only affects compiled structure layout.

Dependencies: Coupled to strace's compatibility type conventions and tests that must be independent of host libc's modern `struct timespec`.

Integration points: Used by time ABI tests to keep expected output stable across 32-bit, 64-bit, and time64-capable hosts.

Risks: Field-width mistakes would make tests validate the wrong ABI layout. Because it intentionally models an old kernel ABI, replacing it with libc `timespec` would be incorrect.

Test signals: Successful compilation of dependent tests and stable old-timespec field decoding.

Source read signal: complete file read for this research pass; file size 20 line(s), 406 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kernel_old_timespec.h -->
