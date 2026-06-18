# sources/test-tools/stress-ng/core-signal.h

Purpose: declares signal utility functions and macro implementations of siglongjmp wrappers needed for portability.

Important APIs/types/functions: declarations cover signal string/name lookup, longjump mask setup, handler install/restore, stop/exit/ignore/default handlers, SIGCHLD handler, SIGALRM pending query, SIGILL/SIGSEGV catchers, and siglongjmp wrappers. `stress_signal_siglongjmp` and `stress_signal_siglongjmp_flag` are macros rather than functions because some Cygwin builds fail when passing `sigjmp_buf` through a function.

Control flow: macro longjump wrappers ignore the signal value, call `siglongjmp`, and mark no-return; the flag variant returns if `*do_jmp` is false and clears it before jumping.

State and persistence: no header-owned state. Functions may install process signal handlers and affect global continue flags.

Dependencies/integration: includes `stress-ng.h` for signal, sigaction, sigset, sigjmp, and stress attributes. Used by stressors that recover from expected SIGSEGV/SIGBUS/SIGILL or need coordinated termination.

Risks: macros evaluate `do_jmp` pointer and jump environment directly; callers must ensure lifetime and volatile semantics. Static buffers in implementation mean string helpers are not thread-safe.

Test signals: Cygwin-compatible builds, longjump recovery stressors, handler restore paths, and fatal signal catchers in forked tests.
