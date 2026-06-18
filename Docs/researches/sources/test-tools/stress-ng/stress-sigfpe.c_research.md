# sources/test-tools/stress-ng/stress-sigfpe.c

Purpose: implements the `sigfpe` stressor, generating integer division by zero, floating division by zero, and `fenv` exceptions, then recovering via `siglongjmp` and optionally verifying signal metadata.

Important APIs/types/functions: `stress_fpehandler`, `stress_sigfpe`, `stress_int_div_by_zero`, `stress_float_div_by_zero`, `feclearexcept`, `feraiseexcept`, `sigaction`, `sigsetjmp`, `siginfo_t`, `FPE_*`, `FE_*`, and SIGILL fallback handling for undefined division behavior.

Control flow: the worker installs handlers for SIGFPE and SIGILL, synchronizes start, cycles through a static list of exception scenarios, establishes a jump point, and either performs the faulting arithmetic/`feraiseexcept` or handles the signal-return path. In verify mode it compares `si_code` with the expected FPE code for SIGFPE and logs SIGILL variants once.

State and persistence behavior: state is global jump buffer, last signal number, optional copied siginfo, and a static index through the exception table. Floating-point exception flags are cleared after each fault and before exit.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, optional verify. It is disabled for uClibc and selected architectures or when `fenv.h`, `float.h`, or `siglongjmp` support is missing.

Risks and test signals: C arithmetic faults are undefined enough that SIGILL or no trap can occur on some platforms. Test signals are successful recovery and bogo increments, unexpected `si_code` in verify mode, handler install failure, or stale floating-point exception state.
