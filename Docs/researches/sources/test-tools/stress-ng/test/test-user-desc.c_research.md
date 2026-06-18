<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-user-desc.c -->
# sources/test-tools/stress-ng/test/test-user-desc.c

Purpose: compile-time availability probe for `struct user_desc` associated with `user-desc`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `asm/ldt.h`, `string.h`; uses types `struct user_desc`; defines `main`; calls `memset`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `asm/ldt.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: architecture-specific asm header probes are intentionally nonportable. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-user-desc.c -->
