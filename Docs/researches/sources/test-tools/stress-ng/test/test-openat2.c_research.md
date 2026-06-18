<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-openat2.c -->
# sources/test-tools/stress-ng/test/test-openat2.c

Purpose: minimal stress-ng configure probe for the Linux openat2 path-resolution syscall; it compiles and often lightly invokes `openat2`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `sys/syscall.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `linux/openat2.h`; uses types `struct open_how`; defines `main`; calls `syscall`; references constants/macros `O_RDWR`, `O_CREAT`, `RESOLVE_NO_SYMLINKS`, `AT_FDCWD`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value direct syscall paths use `__NR_openat2` through `syscall()`.

State and persistence behavior: may create or open a filesystem path using Linux path-resolution flags; any created file is observable host filesystem state if not removed.

Dependencies and integration points: depends on headers `unistd.h`, `sys/syscall.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `linux/openat2.h`; architecture syscall numbers `__NR_openat2`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: direct syscall-number probes are kernel/libc/architecture sensitive and may compile while returning `ENOSYS`, `EINVAL`, or permission errors at runtime. Test signals are successful compilation; successful linking; the expected syscall symbol being present; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-openat2.c -->
