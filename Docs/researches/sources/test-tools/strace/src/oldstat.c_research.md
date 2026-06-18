<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/oldstat.c -->
# sources/test-tools/strace/src/oldstat.c

Purpose: decodes legacy `oldstat` and `oldfstat` syscalls when `struct __old_kernel_stat` is available.

Important APIs/types/functions: `print_old_kernel_stat`, `SYS_FUNC(oldstat)`, `SYS_FUNC(oldfstat)`, `struct __old_kernel_stat`, and normalized `struct strace_stat`.

Control flow: on entry, `oldstat` prints pathname and `oldfstat` prints fd. On exit, both fetch the old kernel stat buffer, normalize fields with sign/zero extension into `strace_stat`, and call `print_struct_stat`.

State and persistence behavior: no persistent state.

Dependencies and integration points: depends on `asm_stat.h`, `stat.h`, old kernel stat configure probes, path/fd printers, and the shared stat structure printer.

Risks: compiled only on platforms exposing the old structure. Legacy field widths and sign extension must match historical ABI expectations.

Test signals: oldstat/oldfstat traces on supported architectures, bad output pointers, timestamp sign extension, device/inode formatting, and absence on unsupported builds.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/oldstat.c -->
