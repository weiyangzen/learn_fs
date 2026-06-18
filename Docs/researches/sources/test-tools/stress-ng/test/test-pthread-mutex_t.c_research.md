<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutex_t.c -->
# sources/test-tools/stress-ng/test/test-pthread-mutex_t.c

Purpose: compile-time availability probe for `pthread_mutex_t` associated with `pthread-mutex_t`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `pthread.h`, `string.h`; uses types `pthread_mutex_t`; defines `main`; calls `memset`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: uses in-process pthread objects, attributes, or scheduling state that ends with process exit.

Dependencies and integration points: depends on headers `pthread.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutex_t.c -->
