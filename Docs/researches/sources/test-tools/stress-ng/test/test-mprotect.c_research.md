<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mprotect.c -->
# sources/test-tools/stress-ng/test/test-mprotect.c

Purpose: minimal stress-ng configure probe for the memory protection API; it compiles and often lightly invokes `mprotect`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdint.h`, `sys/mman.h`; defines `main`; calls `mprotect`; references constants/macros `PROT_READ`, `PROT_WRITE`, `PROT_EXEC`, `PROT_NONE`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: changes page protections for process-local memory and does not persist outside the process.

Dependencies and integration points: depends on headers `stdint.h`, `sys/mman.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: memory-management probes are sensitive to kernel version, page alignment, architecture support, and libc header availability. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mprotect.c -->
