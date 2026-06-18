<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kexec_file_load.c -->
# sources/test-tools/strace/tests/kexec_file_load.c

Purpose: Tests decoding of `kexec_file_load`, including fd arguments, command-line pointer/length combinations, and file-load flags.

Important APIs/types/functions: Uses `syscall(__NR_kexec_file_load)`, local `struct strval`, command-line buffers from `tail_memdup`, `snprintf`, and flag strings for `KEXEC_FILE_*`.

Control flow: Iterates three flag cases and seven command-line pointer/length cases, including NULL, faulting end pointer, truncated long strings, exact NUL-inclusive and NUL-exclusive short strings, and overlong lengths. Each call prints fd truncation, length, command-line rendering, flags, and return code.

State/persistence behavior: No kernel image is loaded because bogus fds and permissions make calls fail. Memory buffers are local.

Dependencies: Requires `__NR_kexec_file_load`; otherwise skipped. Pointer-width conditionals control high-bit flag printing.

Integration points: Validates strace string argument decoding with explicit length, fd scalar rendering, and kexec file flag xlat.

Risks: Privilege-sensitive syscall must stay in failure path. Pointer width changes affect expected flag prefixes.

Test signals: Matrix of `kexec_file_load(...)` lines with quoted command lines, NULL/pointer fallbacks, flag names, and clean exit.

Source read signal: complete file read for this research pass; file size 107 line(s), 2949 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kexec_file_load.c -->
