# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_ras.c

## Purpose

`kern_ras.c` implements restartable atomic sequences (RAS) for user processes on platforms with `__HAVE_RAS`. A registered address range is restarted at its beginning if interrupted while executing inside the range.

## Main Responsibilities

- Maintains per-process `p_raslist` entries.
- Looks up interrupted addresses with `ras_lookup()`.
- Copies RAS registrations on fork with `ras_fork()`.
- Purges all RAS entries with `ras_purgeall()`.
- Installs/removes individual RAS entries through `sys_rasctl()`.

## RAS Lookup

- `ras_lookup(p, addr)` disables preemption, walks `p->p_raslist`, and returns the registered start address if `addr` is strictly inside a RAS range.
- If no match exists, it returns `(void *)-1`.
- No explicit list lock is taken during lookup; the design relies on preemption disable plus `ras_sync()` after mutations.

## Synchronization

- `ras_sync()` forces CPUs through a cross-call barrier when the current process is multithreaded and the system has multiple CPUs.
- Mutation paths update `p_raslist` under `p_auxlock` and call `ras_sync()` before freeing removed entries.

## Install and Purge

- `ras_install()`:
  - rejects zero-length ranges;
  - checks user address range bounds against `VM_MIN_ADDRESS` and `VM_MAXUSER_ADDRESS`;
  - rejects overlapping ranges with `EEXIST`;
  - limits count to `ras_per_proc` (default 16);
  - prepends the new entry to the process list.
- `ras_purge()`:
  - requires exact start address and length match;
  - removes the entry under `p_auxlock`;
  - syncs before freeing;
  - returns `ESRCH` if not found.
- `ras_purgeall()` removes all entries for current process.

## Syscall Interface

- `sys_rasctl()` supports:
  - `RAS_INSTALL`
  - `RAS_PURGE`
  - `RAS_PURGE_ALL`
- If the architecture lacks `__HAVE_RAS`, it returns `EOPNOTSUPP`.
