<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mseal.c -->
# sources/test-tools/stress-ng/test/test-mseal.c

Purpose: minimal stress-ng configure probe for the Linux memory sealing API; it compiles and often lightly invokes `mseal`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `sys/mman.h`; defines `main`; calls `mmap`, `mseal`; references constants/macros `PROT_READ`, `PROT_WRITE`, `MAP_ANONYMOUS`, `MAP_PRIVATE`, `MAP_FAILED`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `unistd.h`, `sys/mman.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: memory-management probes are sensitive to kernel version, page alignment, architecture support, and libc header availability. runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mseal.c -->
