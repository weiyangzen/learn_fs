<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-select.c -->
# sources/test-tools/stress-ng/test/test-select.c

Purpose: minimal stress-ng configure probe for the select event API; it compiles and often lightly invokes `select`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdlib.h`, `sys/select.h`; uses types `struct timeval`; defines `main`; calls `select`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdlib.h`, `sys/select.h`; preprocessor availability gates such as `#if defined(__serenity__)`, `#error Serenity OS does not currently support pselect`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-select.c -->
