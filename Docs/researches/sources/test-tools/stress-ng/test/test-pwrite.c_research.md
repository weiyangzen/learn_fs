<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pwrite.c -->
# sources/test-tools/stress-ng/test/test-pwrite.c

Purpose: minimal stress-ng configure probe for the positional write API; it compiles and often lightly invokes `pwrite`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`; defines `main`; calls `open`, `pwrite`, `close`; references constants/macros `O_WRONLY`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pwrite.c -->
