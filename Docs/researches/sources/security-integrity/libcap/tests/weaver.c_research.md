# sources/security-integrity/libcap/tests/weaver.c

Purpose: shared-object and executable helper that creates threads and reports aggregate keepcaps observations for PSX regression tests.

Important APIs/functions: exports `weaver_thread()`, `weaver_setup()`, `weaver_waitforit()`, and `weaver_terminate()`. `run_thread()` waits for trigger state and adds `PR_GET_KEEPCAPS + 2` to a total. `SO_MAIN()` self-tests ten threads when the shared object is run as executable.

Control flow: condition variables coordinate priming, tick, and exit states. `weaver_waitforit(n)` waits until `n` threads are ready, triggers them, waits for all counters, resets trigger, and returns total.

State and dependencies: static mutex/cond and counters hold shared state. Depends on pthreads, prctl, and `execable.h`.

Risks and test signals: used to prove PSX can discover threads created inside dlopened code not linked directly with libpsx. Expected totals encode keepcaps consistency.
