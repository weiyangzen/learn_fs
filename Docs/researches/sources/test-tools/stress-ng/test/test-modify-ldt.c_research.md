<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-modify-ldt.c -->
# sources/test-tools/stress-ng/test/test-modify-ldt.c

Purpose: minimal stress-ng configure probe for `modify-ldt`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `unistd.h`, `sys/syscall.h`, `sys/types.h`, `asm/ldt.h`, `string.h`; uses types `struct user_desc`; defines `main`; calls `memset`, `syscall`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value direct syscall paths use `__NR_modify_ldt` through `syscall()`.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `unistd.h`, `sys/syscall.h`, `sys/types.h`, `asm/ldt.h`, `string.h`; architecture syscall numbers `__NR_modify_ldt`; preprocessor availability gates such as `#if !defined(__NR_modify_ldt)`, `#error modify_ldt syscall not defined`, `#if defined(__x86_64__) || defined(__x86_64) || \`, `#error modify_ldt syscall not applicable for non-x86 architectures`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: direct syscall-number probes are kernel/libc/architecture sensitive and may compile while returning `ENOSYS`, `EINVAL`, or permission errors at runtime. explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. architecture-specific asm header probes are intentionally nonportable. Test signals are successful compilation; successful linking; the expected syscall symbol being present; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-modify-ldt.c -->
