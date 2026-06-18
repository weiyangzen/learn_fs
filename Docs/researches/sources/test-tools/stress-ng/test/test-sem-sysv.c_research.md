<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sem-sysv.c -->
# sources/test-tools/stress-ng/test/test-sem-sysv.c

Purpose: minimal stress-ng configure probe for the System V semaphore API; it compiles and often lightly invokes `sem-sysv`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `time.h`, `sys/types.h`, `sys/ipc.h`, `sys/sem.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`; uses types `struct semid_ds`, `struct seminfo`, `struct sembuf`, `struct timespec`, `union _semun`; defines `main`; calls `getpid`, `semget`, `semctl`, `clock_gettime`, `semtimedop`, `semop`; references constants/macros `IPC_STAT`, `IPC_SET`, `IPC_INFO`, `IPC_CREAT`, `IPC_RMID`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: allocates a System V semaphore set and removes it through `IPC_RMID`; semaphore values are transient kernel IPC state.

Dependencies and integration points: depends on headers `time.h`, `sys/types.h`, `sys/ipc.h`, `sys/sem.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`; preprocessor availability gates such as `#if defined(__gnu_hurd__)`, `#error semop, semget and semctl are not implemented`, `#if defined(__linux__)`, `#if defined(IPC_STAT)`, `#if defined(SEM_STAT)`, `#if defined(IPC_INFO) &&	\`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sem-sysv.c -->
