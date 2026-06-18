<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/adjtimex.c -->
## sources/test-tools/strace/tests/adjtimex.c

Purpose: Tests decoding of `adjtimex` input/output `timex` structures and return-state names.

Important APIs/types/functions: Uses `k_adjtimex`, `kernel_old_timex_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `printflags(adjtimex_status)`, `printxval(adjtimex_state)`, and `zero_extend_signed_to_ull`.

Control flow: Calls `adjtimex(NULL)`, then allocates and zeroes a kernel timex struct, calls `adjtimex(tx)`, skips if the real syscall is unavailable/fails, and prints all decoded fields plus the returned clock state xlat.

State and persistence: Reads kernel clock discipline state into a temporary buffer; no persistent modification because modes are zero.

Dependencies and integration: Depends on `kernel_old_timex.h` and xlat tables for status and state names.

Risks: Kernel struct layout, signedness, and architecture time ABI can differ. The test avoids setting clock state but still depends on permitted read behavior.

Test signals: Output should show `adjtimex(NULL)`, a full `{modes=0,... tai=...}` structure, named status flags or `0`, and named return state.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/adjtimex.c -->
