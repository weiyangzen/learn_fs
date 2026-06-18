<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mq-posix.c -->
# sources/test-tools/stress-ng/test/test-mq-posix.c

Purpose: minimal stress-ng configure probe for the POSIX message queue API; it compiles and often lightly invokes `mq-posix`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `stdio.h`, `string.h`, `sys/types.h`, `mqueue.h`, `signal.h`, `fcntl.h`; uses types `struct mq_attr`, `struct timespec`, `struct sigevent`, `union sigval`, `mqd_t`; defines `notify_func`, `main`; calls `snprintf`, `getpid`, `mq_open`, `memset`, `mq_notify`, `mq_timedreceive`, `mq_receive`, `mq_getattr`, `mq_timedsend`, `mq_send`, `mq_close`, `mq_unlink`; references constants/macros `O_CREAT`, `O_RDWR`, `SIGEV_THREAD`.

Control flow: helper definitions `notify_func` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: creates a named POSIX message queue and removes it with `mq_unlink`; queue attributes and pending messages are transient kernel state.

Dependencies and integration points: depends on headers `unistd.h`, `stdio.h`, `string.h`, `sys/types.h`, `mqueue.h`, `signal.h`, `fcntl.h`; preprocessor availability gates such as `#if defined(__gnu_hurd__)`, `#error posix message queues not implemented on GNU/HURD`, `#if defined(__FreeBSD_kernel__)`, `#error posix message queues not implemented with FreeBSD kernel`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. path names derived from `argv[0]` can include slashes or unusual characters when the probe is launched from uncommon build harnesses. runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking; a complete type size; message-queue library compatibility where the platform still requires `-lrt`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mq-posix.c -->
