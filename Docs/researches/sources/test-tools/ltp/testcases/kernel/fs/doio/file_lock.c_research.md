# sources/test-tools/ltp/testcases/kernel/fs/doio/file_lock.c

Purpose: `file_lock.c` provides small retrying wrappers around `fcntl()` record locks for the doio and growfiles stress programs. It supports whole-file locks and explicit byte-range locks, normalizing the lock flag interface used by the legacy tests.

Important APIs and types: public functions are `file_lock(int fd, int flags, char **errormsg)` and `record_lock(int fd, int flags, int start, int len, char **errormsg)`. The module exports `Fl_syscall_str[128]`, a diagnostic string describing the most recent `fcntl()` call, and uses an internal static `errmsg[256]`. It consumes `LOCK_NB`, `LOCK_UN`, `LOCK_EX`, and `LOCK_SH` from `file_lock.h` or system headers.

Control flow: both functions zero a `struct flock`, choose `F_SETLK` for nonblocking locks or `F_SETLKW` for blocking locks, set `l_whence = 0`, and select `F_UNLCK`, `F_WRLCK`, or `F_RDLCK` from the caller flags. `file_lock()` uses `l_start = 0` and `l_len = 0` for the whole file; `record_lock()` uses caller-supplied `start` and `len`. Invalid lock mode flags set `errno = EINVAL`, populate `errormsg`, and return `-1`.

State and persistence behavior: locks persist in the kernel according to normal POSIX advisory-lock semantics and are released by unlock calls, descriptor close, or process exit. User-visible module state is limited to `Fl_syscall_str` and the static error buffer; both are overwritten by each call and are not thread-safe.

Dependencies and integration points: `growfiles.c` calls `file_lock()` through `lkfile()` for optional lock levels around write/read/truncate cycles or entire open/close windows. `doio.c` implements its own local region-lock helper rather than using this file. The wrappers depend on `fcntl` behavior and platform errno values, including optional legacy `EFILESH` and local fallback `EFSEXCLWR`.

Risks: retry behavior is surprising: for `F_SETLK`, several errors including `EACCES` and `EINTR` are retried indefinitely, which can spin rather than returning a nonblocking failure. The comment says it loops when `LOCK_NB` is not set, but the retry switch is under `cmd == F_SETLK`; that mismatch is a maintenance hazard. Error strings use fixed buffers and `sprintf`. The functions accept inconsistent flag combinations without checking for multiple lock mode bits beyond first-match ordering.

Test signals: useful checks include exclusive/shared/unlock success across cooperating processes, range-lock conflict behavior, invalid flag rejection with `EINVAL`, and interruption behavior. Stress tests should monitor for CPU spin when nonblocking locks encounter persistent `EACCES` or protected-file errors.
