<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mtx-init.c -->
# sources/test-tools/stress-ng/test/test-mtx-init.c

Purpose: minimal stress-ng configure probe for the C11 threads mutex API; it compiles and often lightly invokes `mtx-init`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `threads.h`, `string.h`; uses types `mtx_t`; defines `main`; calls `memset`, `mtx_init`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses stack-allocated C11 mutex state only.

Dependencies and integration points: depends on headers `threads.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mtx-init.c -->
