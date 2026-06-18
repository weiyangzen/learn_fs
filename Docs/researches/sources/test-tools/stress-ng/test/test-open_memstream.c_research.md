<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-open_memstream.c -->
# sources/test-tools/stress-ng/test/test-open_memstream.c

Purpose: minimal stress-ng configure probe for `open_memstream`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `stddef.h`, `stdio.h`; defines `main`; calls `open_memstream`, `fprintf`, `fclose`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `stddef.h`, `stdio.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-open_memstream.c -->
