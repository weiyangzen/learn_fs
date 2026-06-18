<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_sigevent.c -->
# sources/test-tools/strace/src/print_sigevent.c

Purpose: mpers-aware printer for `struct sigevent`.

Important APIs/types/functions: `print_sigevent`, `print_sigev_value`, `struct_sigevent`, and `sigev_value` xlat.

Control flow: fetches the structure, optionally prints non-null `sigev_value`, prints `sigev_signo` as a signal for signal/thread/thread-id notifications, prints notify type, and then prints thread id or thread callback/attribute pointers for relevant modes.

State and persistence behavior: no state.

Dependencies and integration points: used by timer, AIO, and message queue decoders; depends on mpers, `sigevent.h`, signal names, and generated notify xlats.

Risks: union field macros are layout-sensitive. Unknown notify modes print numeric signal and omit union-specific fields.

Test signals: SIGEV_SIGNAL, SIGEV_NONE, SIGEV_THREAD, SIGEV_THREAD_ID, non-null sigev_value, invalid pointer, and compat layouts.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_sigevent.c -->
