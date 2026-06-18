<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-msync.c -->
# sources/test-tools/stress-ng/test/test-msync.c

Purpose: minimal stress-ng configure probe for the memory-map synchronization API; it compiles and often lightly invokes `msync`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `string.h`, `unistd.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `sys/mman.h`; defines `main`; calls `memset`, `open`, `unlink`, `write`, `mmap`, `msync`, `munmap`, `close`; references constants/macros `O_RDWR`, `O_CREAT`, `PROT_READ`, `PROT_WRITE`, `MAP_PRIVATE`, `MAP_FAILED`, `MS_ASYNC`, `MS_SYNC`, `MS_INVALIDATE`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value error handling uses a compact cleanup label so opened descriptors or mappings are released before returning failure.

State and persistence behavior: uses temporary filesystem objects and file descriptors, usually unlinking the name after opening so data should not persist after close.

Dependencies and integration points: depends on headers `string.h`, `unistd.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `sys/mman.h`; preprocessor availability gates such as `#if defined(__gnu_hurd__)`, `#error msync is defined but not implemented and will always fail`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. memory-management probes are sensitive to kernel version, page alignment, architecture support, and libc header availability. runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-msync.c -->
