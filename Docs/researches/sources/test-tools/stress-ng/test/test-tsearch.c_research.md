<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-tsearch.c -->
# sources/test-tools/stress-ng/test/test-tsearch.c

Purpose: minimal stress-ng configure probe for the tree-search API; it compiles and often lightly invokes `tsearch`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `search.h`, `stdlib.h`, `string.h`; defines `cmp`, `main`; calls `tsearch`, `tdelete`.

Control flow: helper definitions `cmp` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `search.h`, `stdlib.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-tsearch.c -->
