<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_kernel_sigset.c -->
# sources/test-tools/strace/src/print_kernel_sigset.c

Purpose: mpers-aware printer for structures containing a signal-set pointer and size.

Important APIs/types/functions: `print_kernel_sigset`, `struct_sigset_addr_size`, and `print_sigset_addr_len`.

Control flow: fetches the two-field structure from tracee memory, prints `sigmask` by dereferencing the pointed-to sigset with the provided size, then prints `sigsetsize`.

State and persistence behavior: no state.

Dependencies and integration points: used by syscalls that pass a packed `{sigmask, sigsetsize}` pointer; depends on mpers pointer sizing and generic sigset printers.

Risks: pointer fields are personality-sensitive. Invalid outer or inner pointers must fall back cleanly.

Test signals: native and compat layouts, NULL sigmask, invalid pointers, different sigset sizes, and signal names.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_kernel_sigset.c -->
