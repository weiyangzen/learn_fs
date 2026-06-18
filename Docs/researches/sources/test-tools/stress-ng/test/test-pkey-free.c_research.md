<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pkey-free.c -->
# sources/test-tools/stress-ng/test/test-pkey-free.c

Purpose: minimal stress-ng configure probe for the memory-protection-key release API; it compiles and often lightly invokes `pkey-free`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/mman.h`, `unistd.h`, `features.h`; defines `main`; calls `pkey_free`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/mman.h`, `unistd.h`, `features.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: memory-management probes are sensitive to kernel version, page alignment, architecture support, and libc header availability. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pkey-free.c -->
