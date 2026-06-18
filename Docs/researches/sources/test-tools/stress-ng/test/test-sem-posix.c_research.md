<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sem-posix.c -->
# sources/test-tools/stress-ng/test/test-sem-posix.c

Purpose: minimal stress-ng configure probe for `sem-posix`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `time.h`, `semaphore.h`; uses types `struct timespec`; defines `main`; calls `sem_init`, `sem_wait`, `sem_post`, `sem_trywait`, `sem_timedwait`, `sem_destroy`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `time.h`, `semaphore.h`; preprocessor availability gates such as `#if defined(__FreeBSD_kernel__)`, `#error POSIX semaphores not yet implemented`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sem-posix.c -->
