# sources/test-tools/strace/src/kexec.c

Purpose: decodes `kexec_load` and `kexec_file_load` syscalls.

Important APIs/types/functions: `SYS_FUNC(kexec_load)`, `SYS_FUNC(kexec_file_load)`, `print_seg`, `print_kexec_segments`, `KEXEC_SEGMENT_MAX`, `KEXEC_ARCH_MASK`, and xlats `kexec_load_flags`, `kexec_arch_values`, `kexec_file_load_flags`.

Control flow: `kexec_load` prints entry address, segment count, bounded segment array, and flags split into architecture mask plus remaining load flags. `print_seg` adapts fetched segment elements for compat word sizes. `kexec_file_load` prints kernel/initrd fds, command-line length and string, and file-load flags.

State and persistence behavior: no persistent state. Reads tracee memory for segment arrays and command line strings only.

Dependencies and integration points: depends on `<linux/kexec.h>`, fd/path string printers, current tracee word size, and generated xlat tables.

Risks: segment arrays are trusted only up to `KEXEC_SEGMENT_MAX`; larger counts fall back to an address. Compat segment element sizing must match current word size.

Test signals: cover native and compat segment arrays, oversized segment count fallback, architecture flags combined with load flags, command-line truncation by length, and invalid fds/pointers.
