<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/desc.c -->
## sources/test-tools/strace/src/desc.c

Purpose: Decodes descriptor-related syscalls in this file: `close`, `select`, old indirect `select`, Alpha `osf_select`, and `pselect6` time32/time64 variants.

Important APIs and types: `fd_set_arg_name`, `SYS_FUNC(close)`, `decode_select`, `SYS_FUNC(oldselect)`, `SYS_FUNC(osf_select)`, `SYS_FUNC(select)`, `do_pselect6`, `SYS_FUNC(pselect6_time32)`, and `SYS_FUNC(pselect6_time64)`.

Control flow: `close` prints fd. `decode_select` normalizes `nfds`, caps very large values to avoid excessive memory, computes fdset byte size from `current_wordsize`, prints fd bitsets and timeout on entry, then on successful exit builds an aux string describing ready input/output/exception fds and remaining timeout. `do_pselect6` appends the sigmask argument after select decoding.

State and persistence: Uses a static `outstr[1024]` for select aux strings. No per-tcb private state.

Dependencies and integration: Depends on `defs.h`, `xstring.h`, fd printing, bitset scanning, time/time32/time64 printers, and indirect syscall argument fetching.

Risks: Select fdset decoding is sensitive to `nfds`, word size, malloc failures, and output truncation. The static aux buffer is overwritten by subsequent calls.

Test signals: Tests should include negative and huge `nfds`, null fdsets, ready fd output, timeout output, abbrev/verbose behavior, pselect sigmask, oldselect indirect args, and compat word sizes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/desc.c -->
