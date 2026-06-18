<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-posix-fallocate.c -->
# sources/test-tools/stress-ng/test/test-posix-fallocate.c

Purpose: minimal stress-ng configure probe for the file allocation API; it compiles and often lightly invokes `posix-fallocate`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `fcntl.h`; defines `main`; calls `open`, `unlink`, `posix_fallocate`, `close`; references constants/macros `O_RDWR`, `O_CREAT`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses temporary filesystem objects and file descriptors, usually unlinking the name after opening so data should not persist after close.

Dependencies and integration points: depends on headers `unistd.h`, `fcntl.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-posix-fallocate.c -->
