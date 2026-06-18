<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-qsort.c -->
# sources/test-tools/stress-ng/test/test-qsort.c

Purpose: minimal stress-ng configure probe for the libc qsort API; it compiles and often lightly invokes `qsort`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdlib.h`, `stdio.h`; defines `cmp`, `main`; calls `qsort`.

Control flow: helper definitions `cmp` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdlib.h`, `stdio.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-qsort.c -->
