# sources/object-store/openstack-swift/swift/common/utils/libc.py

## Purpose

`libc.py` isolates Swift's direct interactions with libc and Linux-specific low-level APIs. It provides lazy libc function lookup, cache-dropping advisory calls, Linux AF_ALG MD5 socket setup, process nice/ionice priority modification, and exported constants used by diskfile and daemon code.

## Important APIs, Types, And Functions

- Global lazy handles include `_posix_fadvise`, `_libc_socket`, `_libc_bind`, `_libc_accept`, `_libc_setpriority`, and `_posix_syscall`.
- `NR_ioprio_set()` returns the architecture-specific Linux syscall number for `ioprio_set` on x86_64 and aarch64, otherwise raises `OSError`.
- `IOPRIO_PRIO_VALUE(class_, data)` composes Linux ionice class and priority bits.
- Constants include `PRIO_PROCESS`, `IOPRIO_WHO_PROCESS`, `IO_CLASS_ENUM`, `IOPRIO_CLASS_SHIFT`, `AF_ALG`, and `F_SETPIPE_SZ`.
- `noop_libc_function()` is the no-op fallback for missing optional functions.
- `load_libc_function(func_name, log_error=True, fail_if_missing=False, errcheck=False)` loads a libc function, optionally raising when absent and optionally adding an errno-checking `errcheck`.
- `_LibcWrapper` is a lazy callable wrapper exposing `.available` and raising `NotImplementedError` when the function cannot be loaded.
- `drop_buffer_cache(fd, offset, length)` calls `posix_fadvise64(..., POSIX_FADV_DONTNEED)`.
- `sockaddr_alg` models Linux AF_ALG socket address data.
- `get_md5_socket()` returns an accepted AF_ALG MD5 socket fd for callers to write data and read a 16-byte digest.
- `modify_priority(conf, logger)` applies `nice_priority`, `ionice_class`, and `ionice_priority` settings to the current process.

## Control Flow And Behavior

`load_libc_function()` loads libc with `use_errno=True` each time it needs a symbol. Missing functions either raise `AttributeError`, log a warning and return `noop_libc_function`, or silently return the no-op depending on arguments. When `errcheck=True`, a wrapper raises `OSError(ctypes.get_errno(), os.strerror(errcode))` for `-1` results.

`_LibcWrapper` defers symbol lookup until `.available` or `__call__()` is used. It marks itself loaded after the first attempt and caches the handle when found. Missing functions make `.available` false and calls raise `NotImplementedError`, which lets higher-level code choose fallbacks without repeated libc lookups.

`drop_buffer_cache()` lazily loads `posix_fadvise64`, calls it with offset/length as unsigned 64-bit values and advice `4` (`POSIX_FADV_DONTNEED`), and logs a warning for nonzero return values.

`get_md5_socket()` lazily loads `accept`, `socket`, and `bind`. On the first call it creates one bound AF_ALG `"hash"`/`"md5"` socket and stores it in `_bound_md5_sockfd`. Each call then accepts a new operation socket from the bound socket and returns the raw fd. Callers are responsible for closing returned fds.

`modify_priority()` lazily loads `setpriority` with errno checking and applies `nice_priority` if configured. It then lazily loads `syscall` and, when `ionice_class` is configured, computes the Linux `ioprio_set` argument and calls the syscall for the current pid. Invalid classes, priorities, unsupported architectures, and OS errors are caught, printed as warnings, and logged with exceptions.

## State And Persistence

The module holds process-global cached libc handles and one cached bound MD5 AF_ALG socket fd. It mutates process scheduling state through `setpriority` and `ioprio_set`. It issues advisory kernel calls for page cache dropping. It does not write persistent files, but leaked raw fds would persist for the process lifetime.

## Dependencies And Integration Points

Dependencies are standard `ctypes`, `ctypes.util`, `fcntl`, `logging`, `os`, `platform`, and `socket`. `__init__.py` re-exports `F_SETPIPE_SZ`, `load_libc_function`, `drop_buffer_cache`, `get_md5_socket`, `modify_priority`, and `_LibcWrapper`. Object diskfile code imports `get_md5_socket` and `F_SETPIPE_SZ`; daemon and WSGI startup call `modify_priority`; common utils uses `_LibcWrapper` for fallocate wrappers; diskfile or storage code can call `drop_buffer_cache()` after streaming file data.

## Risks And Edge Cases

- The module is Linux-heavy. `NR_ioprio_set()` only supports x86_64 and aarch64 64-bit systems.
- `get_md5_socket()` exposes a raw file descriptor; callers must close it exactly once. Failure leaks fds.
- AF_ALG constants and `sockaddr_alg` structure are Linux-specific; unsupported kernels or missing algorithms raise IOErrors during setup.
- `_bound_md5_sockfd` is shared process-wide and never explicitly closed; this is intentional for reuse but must be acceptable for daemon lifecycle.
- `load_libc_function()` catches only `AttributeError`, not failures to load libc itself.
- `drop_buffer_cache()` treats missing `posix_fadvise64` as a no-op via `load_libc_function()` but still logs return-code warnings for real calls.
- `modify_priority()` prints to stdout/stderr as well as logging exceptions, which can be noisy in daemonized contexts but preserves operator visibility.
- `IOPRIO_PRIO_VALUE()` and `IO_CLASS_ENUM` do not validate Linux priority range beyond integer conversion.

## Test Signals

No local tests are present in this snapshot. Expected coverage should mock libc loading and function return values for `load_libc_function()` and `_LibcWrapper`, verify errno propagation, test `NR_ioprio_set()` architecture branches, confirm `drop_buffer_cache()` argument conversion and warning behavior, simulate AF_ALG socket/bind/accept failures and success in `get_md5_socket()`, and assert `modify_priority()` handles valid settings, invalid class/priority, unsupported architecture, and syscall errors without crashing daemon startup.
