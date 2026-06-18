<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/delay.h -->
## sources/test-tools/strace/src/delay.h

Purpose: Declares the delay-injection API shared between qualifier parsing and the tracing loop.

Important APIs and types: `alloc_delay_data`, `fill_delay_data`, `is_delay_timer_armed`, `delay_timer_expired`, `arm_delay_timer`, and `delay_tcb`.

Control flow: Header-only declarations; callers allocate/fill delay slots and later arm or clear the timer as tracees are delayed and resumed.

State and persistence: State is implemented in `delay.c`.

Dependencies and integration: Requires `struct tcb`, `struct timespec`, `uint16_t`, and `bool` from common headers.

Risks: Callers must use valid delay indices returned by `alloc_delay_data`.

Test signals: Compile coverage plus delay injection tests validate this contract.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/delay.h -->
