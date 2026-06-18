<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat2/openat201.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/openat2/openat201.c

Purpose: Basic :manpage:`openat2(2)` test.

Important APIs/types/functions: includes `fcntl.h`, `tst_test.h`, `lapi/openat2.h`; exercises `openat2`, `fcntl`; defines `cleanup`, `setup`, `run`; uses flags/constants `AT_FDCWD`, `O_CREAT`, `O_DIRECTORY`, `O_RDONLY`, `O_RDWR`, `O_WRONLY`, `RESOLVE_BENEATH`, `RESOLVE_IN_ROOT`, `RESOLVE_NO_MAGICLINKS`, `RESOLVE_NO_SYMLINKS`, `RESOLVE_NO_XDEV`.

Control flow centers on `cleanup`, `setup`, `run`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.cleanup`, `.needs_tmpdir` into the LTP runner.

State and persistence behavior: Runtime state is `struct open_how` resolution policy, directory file descriptors, symlink/magic-link fixtures, mount boundaries, and file descriptors returned by the raw `openat2` syscall.

Dependencies and integration points: Depends on `lapi/openat2.h`, raw syscall availability, `struct open_how`, root/mount fixtures for resolution flags, and Linux 5.6-era openat2 semantics. Direct include dependencies include `fcntl.h`, `tst_test.h`, `lapi/openat2.h`.

Risks and test signals: Resolution-constraint failures depend on exact kernel `openat2()` semantics and fixture layout; unsupported kernels must skip rather than fail. Test signals: reports through `TFAIL`, `TPASS`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat2/openat201.c -->
