<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timer-create.c -->
# sources/test-tools/stress-ng/test/test-timer-create.c

Purpose: minimal stress-ng configure probe for the POSIX timer API; it compiles and often lightly invokes `timer-create`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `signal.h`, `time.h`; uses types `struct sigevent`; defines `main`; calls `timer_create`, `clock_settime`; references constants/macros `SIGEV_SIGNAL`, `SIGRTMIN`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: creates a POSIX timer object whose expiration state lives only until deletion/process exit.

Dependencies and integration points: depends on headers `signal.h`, `time.h`; preprocessor availability gates such as `#if defined(CLOCK_REALTIME)`, `#error no POSIX clock types CLOCK_REALTIME or CLOCK_MONOTONIC`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timer-create.c -->
