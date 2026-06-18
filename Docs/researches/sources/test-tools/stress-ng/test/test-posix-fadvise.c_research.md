<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-posix-fadvise.c -->
# sources/test-tools/stress-ng/test/test-posix-fadvise.c

Purpose: minimal stress-ng configure probe for the POSIX file advice API; it compiles and often lightly invokes `posix-fadvise`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `fcntl.h`; defines `main`; calls `open`, `unlink`, `posix_fadvise`, `endif`, `close`; references constants/macros `O_RDWR`, `O_CREAT`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses temporary filesystem objects and file descriptors, usually unlinking the name after opening so data should not persist after close.

Dependencies and integration points: depends on headers `unistd.h`, `fcntl.h`; preprocessor availability gates such as `#if defined(__gnu_hurd__)`, `#error posix_fadvise is defined but not implemented and will always fail`, `#if defined(POSIX_FADV_NORMAL)`, `#if defined(POSIX_FADV_SEQUENTIAL)`, `#if defined(POSIX_FADV_RANDOM)`, `#if defined(POSIX_FADV_NOREUSE)`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-posix-fadvise.c -->
