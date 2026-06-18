<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-posix-openpt.c -->
# sources/test-tools/stress-ng/test/test-posix-openpt.c

Purpose: minimal stress-ng configure probe for the pseudo-terminal master open API; it compiles and often lightly invokes `posix-openpt`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdlib.h`, `fcntl.h`; defines `main`; calls `posix_openpt`; references constants/macros `O_RDWR`, `O_NOCTTY`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `stdlib.h`, `fcntl.h`; preprocessor availability gates such as `#if !defined(_XOPEN_SOURCE)`, `#if defined(O_RDWR)`, `#if defined(O_RDWR)`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-posix-openpt.c -->
