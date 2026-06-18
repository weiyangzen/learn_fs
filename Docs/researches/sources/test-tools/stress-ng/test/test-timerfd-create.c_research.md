<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timerfd-create.c -->
# sources/test-tools/stress-ng/test/test-timerfd-create.c

Purpose: minimal stress-ng configure probe for the timerfd API; it compiles and often lightly invokes `timerfd-create`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/timerfd.h`; defines `main`; calls `timerfd_create`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: creates a timer file descriptor whose expiration state lives only until close/process exit.

Dependencies and integration points: depends on headers `sys/timerfd.h`; preprocessor availability gates such as `#if defined(CLOCK_REALTIME)`, `#error no POSIX clock types CLOCK_REALTIME or CLOCK_MONOTONIC`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timerfd-create.c -->
