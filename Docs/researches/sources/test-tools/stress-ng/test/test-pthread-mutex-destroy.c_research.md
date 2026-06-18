<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutex-destroy.c -->
# sources/test-tools/stress-ng/test/test-pthread-mutex-destroy.c

Purpose: minimal stress-ng configure probe for the pthread API; it compiles and often lightly invokes `pthread-mutex-destroy`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `pthread.h`, `string.h`; uses types `pthread_mutex_t`; defines `main`; calls `pthread_mutex_destroy`; references constants/macros `PTHREAD_MUTEX_INITIALIZER`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses in-process pthread objects, attributes, or scheduling state that ends with process exit.

Dependencies and integration points: depends on headers `pthread.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking; pthread link compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutex-destroy.c -->
