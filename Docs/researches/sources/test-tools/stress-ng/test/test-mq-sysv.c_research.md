<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mq-sysv.c -->
# sources/test-tools/stress-ng/test/test-mq-sysv.c

Purpose: minimal stress-ng configure probe for the System V message queue API; it compiles and often lightly invokes `mq-sysv`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `stdio.h`, `string.h`, `sys/types.h`, `sys/stat.h`, `sys/ipc.h`, `sys/msg.h`; uses types `struct msqid_ds`, `struct msginfo`; defines `main`; calls `MAX_SIZE`, `msgget`, `memset`, `strncpy`, `msgsnd`, `msgrcv`, `msgctl`; references constants/macros `IPC_PRIVATE`, `IPC_CREAT`, `IPC_EXCL`, `IPC_STAT`, `IPC_RMID`, `IPC_INFO`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: allocates a System V message queue and requests cleanup with `IPC_RMID`; message contents and queue metadata are transient kernel IPC state.

Dependencies and integration points: depends on headers `unistd.h`, `stdio.h`, `string.h`, `sys/types.h`, `sys/stat.h`, `sys/ipc.h`, `sys/msg.h`; preprocessor availability gates such as `#if defined(__gnu_hurd__)`, `#error msgsnd, msgrcv, msgget, msgctl are not implemented`, `#if defined(__linux__)`, `#if defined(__linux__)`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mq-sysv.c -->
