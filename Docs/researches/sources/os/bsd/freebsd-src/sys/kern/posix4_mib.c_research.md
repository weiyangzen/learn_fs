# File Research: sources/os/bsd/freebsd-src/sys/kern/posix4_mib.c

## Purpose
Implements the FreeBSD POSIX.1B (`p1003_1b`) sysctl MIB values used by `sysconf(3)` and related consumers to discover realtime/POSIX feature support and limits.

## Key Elements
- `facility[]` stores configured POSIX.1B feature or limit values indexed by `CTL_P1003_1B_* - 1`.
- `facility_initialized[]` records whether each value has been explicitly set.
- `P1B_SYSCTL()` declares read-only integer sysctls under `_p1003_1b`.
- `P1B_SYSCTL_RW()` declares writable sysctls using `p31b_sysctl_proc()`.
- Declared nodes cover asynchronous I/O, mapped files, memory locking/protection, message passing, prioritized I/O, priority scheduling, realtime signals, semaphores, fsync, shared memory objects, synchronized I/O, timers, AIO limits, page size, signal queue limits, timer limits, and semaphore limits.
- `p31b_setcfg()`, `p31b_unsetcfg()`, `p31b_getcfg()`, and `p31b_iscfg()` are the kernel API for feature configuration.
- `p31b_set_standard()` marks always-supported features such as fsync, mapped files, shared memory objects, and page size.

## Sysctl Behavior
Most entries are read-only, capability-readable integer sysctls. `sem_nsems_max` is writable through `p31b_sysctl_proc()`, but only updates `facility[]` if the value was already initialized. Invalid facility indexes are rejected with `EINVAL`.

## Integration
`p1003_1b.c` and other POSIX realtime modules call `p31b_setcfg()` to advertise optional feature support and limits. Userland sees these values through the `_p1003_1b` sysctl namespace.

## Filesystem / VM Relevance
The file exposes feature flags for `fsync`, mapped files, memory protection, page size, and shared memory objects. These are not implementations of those features, but they are user-visible capability declarations relevant to filesystem and VM behavior.

## Notable Edge Cases
- The code keeps `_p1003_1b` as a top-level sysctl namespace because `OID_AUTO` was noted as incompatible with `sysconf(3)` lookup-by-number behavior.
- `p31b_unsetcfg()` does not validate the number before indexing, unlike `p31b_setcfg()` and readers.
