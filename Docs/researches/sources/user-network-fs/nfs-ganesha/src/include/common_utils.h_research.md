# sources/user-network-fs/nfs-ganesha/src/include/common_utils.h

## Purpose
`common_utils.h` is a central utility contract for NFS-Ganesha C code. It collects portability shims, compile-time checks, thread/lock wrappers with logging, time helpers, DNS/statistics wrappers, byte-buffer comparison, and strict small integer parsing. Because it is included widely by SAL, FSAL, logging, idmapper, RPC, and test code, changes here have cross-tree effects.

## Important APIs, Types, And Functions
The header exposes global pthread attributes (`default_mutex_attr`, `default_rwlock_attr`) and the global `PTHREAD_stack_size` used by the `PTHREAD_create` wrapper. `BUILD_BUG_ON`, `ARRAY_SIZE`, `CONCAT`, `UNUSED`, `SCANDIR_CONST`, and `HAVE_MNTENT_H` are compile-time/platform helpers. The pthread wrappers (`PTHREAD_MUTEX_*`, `PTHREAD_RWLOCK_*`, `PTHREAD_COND_*`, `PTHREAD_SPIN_*`, and attribute wrappers) wrap POSIX primitives, log to `COMPONENT_RW_LOCK`, and abort on unexpected errors. Inline helpers include `PTHREAD_mutex_trylock`, `PTHREAD_cond_timedwait`, `timespec_diff`, `timespec_update`, `timespec_to_nsecs`, `nsecs_to_timespec`, `timespec_add_nsecs`, `timespec_sub_nsecs`, `gsh_time_cmp`, `gsh_buffdesc_comparator`, `now`, `now_mono`, `gsh_gethostname`, `gsh_getaddrinfo`, `gsh_getnameinfo`, and `parse_uint16_from_str`.

## Control Flow
The lock/condition wrappers are macros, so control flow is injected at call sites: call POSIX primitive, log on success at full debug, log critical and `abort()` on non-recoverable return values. `PTHREAD_mutex_trylock` and `PTHREAD_cond_timedwait` are softer wrappers that treat `EBUSY` and `ETIMEDOUT` as expected outcomes. `PTHREAD_create` initializes a scratch attr if needed, applies the configured stack size, and delegates to `pthread_create`.

## State And Persistence
The header does not persist data to disk. It depends on external global state for logging levels, default pthread attributes, DNS statistics, and thread stack size. Time helpers read system clocks. `timespec_update` writes `tv_sec` and `tv_nsec` via atomic stores to allow low-cost publication of timestamp snapshots.

## Dependencies And Integration Points
It depends on libc/POSIX headers, `abstract_atomic.h`, `gsh_types.h`, `log.h`, and later `idmapper.h` for DNS statistics. It is foundational for code that uses the project-specific pthread wrappers, including the thread fridge, export manager, delayed executor, FSAL, connection manager, and logging code.

## Risks
Macro wrappers evaluate pointer arguments once but still change debugging and abort semantics globally. The wrappers assume most pthread errors are fatal, which is appropriate for core locks but risky for code that might otherwise recover. `config_error_no_error`-style aliasing is not here, but this file does perform atomic stores through casted `timespec` fields and assumes field sizes match `uint64_t`. `parse_uint16_from_str` relies on `errno`, so callers must include the correct headers through existing transitive includes. `timespec_sub_nsecs` computes `tv_nsec = ts.tv_nsec - t->tv_nsec` in the borrow case, which is unusual and should be tested before reuse in new code.

## Test Signals
Useful tests include compile-only checks for platform shims, lock-wrapper smoke tests under high log levels, timed-wait tests for `ETIMEDOUT`, thread creation tests honoring `PTHREAD_stack_size`, strict parser cases for empty strings, trailing characters, overflow, and `UINT16_MAX`, and time arithmetic tests across second/nanosecond boundaries. Existing usage in `support/fridgethr.c`, `support/delayed_exec.c`, `support/exports.c`, `log/display.c`, and FSAL tests gives integration coverage.
