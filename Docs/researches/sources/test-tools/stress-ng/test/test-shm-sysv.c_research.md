<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-shm-sysv.c -->
# sources/test-tools/stress-ng/test/test-shm-sysv.c

Purpose: minimal stress-ng configure probe for the System V shared-memory API; it compiles and often lightly invokes `shm-sysv`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `sys/ipc.h`, `sys/shm.h`, `sys/stat.h`, `fcntl.h`; uses types `struct shmid_ds`, `struct shminfo`, `struct shm_info`; defines `main`; calls `getpid`, `shmget`, `shmat`, `shmctl`, `endif`, `shmdt`; references constants/macros `IPC_CREAT`, `IPC_EXCL`, `IPC_STAT`, `IPC_INFO`, `IPC_RMID`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: allocates a System V shared-memory segment and removes it through `IPC_RMID`; attachment state is transient.

Dependencies and integration points: depends on headers `unistd.h`, `sys/ipc.h`, `sys/shm.h`, `sys/stat.h`, `fcntl.h`; preprocessor availability gates such as `#if defined(IPC_STAT)`, `#if defined(__linux__) &&	\`, `#if defined(__linux__) &&	\`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-shm-sysv.c -->
