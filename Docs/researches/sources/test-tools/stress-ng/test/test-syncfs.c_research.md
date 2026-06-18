<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-syncfs.c -->
# sources/test-tools/stress-ng/test/test-syncfs.c

Purpose: minimal stress-ng configure probe for the per-filesystem sync API; it compiles and often lightly invokes `syncfs`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`; defines `main`; calls `open`, `unlink`, `syncfs`, `close`; references constants/macros `O_RDWR`, `O_CREAT`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value error handling uses a compact cleanup label so opened descriptors or mappings are released before returning failure.

State and persistence behavior: uses temporary filesystem objects and file descriptors, usually unlinking the name after opening so data should not persist after close.

Dependencies and integration points: depends on headers `unistd.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`; preprocessor availability gates such as `#if defined(__FreeBSD_kernel__)`, `#error syncfs is not implemented with FreeBSD kernel`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-syncfs.c -->
