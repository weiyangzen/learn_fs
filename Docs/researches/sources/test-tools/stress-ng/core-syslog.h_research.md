# sources/test-tools/stress-ng/core-syslog.h

## Purpose
`core-syslog.h` provides portability wrappers around syslog APIs so logging call sites can compile even when `<syslog.h>` is unavailable.

## Important APIs, Types, And Functions
When `HAVE_SYSLOG_H` is defined, `shim_syslog`, `shim_openlog`, and `shim_closelog` map directly to `syslog`, `openlog`, and `closelog`. Otherwise they expand to no-op macros.

## Control Flow
There is no runtime control flow in the header. Preprocessor feature detection selects real syslog calls or no-op behavior at compile time.

## State And Persistence
With syslog support, process logging can persist to the host logging system according to syslog configuration. Without support, no state is stored and calls disappear at compile time.

## Dependencies And Integration Points
It depends on `HAVE_SYSLOG_H` from configure/build detection and on callers including system syslog definitions when available through the common headers. It integrates with stress-ng's `--syslog` behavior and long-running coverage scripts that enable syslog logging.

## Risks
The variadic `shim_syslog` macro requires at least one variadic argument in supported builds. In unsupported builds, logging side effects inside arguments vanish because the macro expands to nothing. Callers must not rely on syslog calls for required control flow.

## Test Signals
Compile tests on systems with and without syslog are the main signal. Runtime coverage comes from `kernel-coverage.sh` and stress-ng invocations with `--syslog`.
