# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_uidinfo.c

## Scope

- Source file read completely: `sources/os/bsd/netbsd-src/sys/kern/kern_uidinfo.c`.
- Subset scope: `Docs/research_subset_a.md`.
- This file implements per-UID resource accounting and sysctl exposure.

## Purpose And Main Interfaces

- Initialization:
  - `uid_init`
- UID lookup:
  - `uid_find`
- Resource counter updates:
  - `chgproccnt`
  - `chglwpcnt`
  - `chgsemcnt`
  - `chgsbsize`
- Sysctl and hash statistics:
  - `kern.uidinfo.{proccnt,lwpcnt,lockcnt,semcnt,sbsize}`
  - `uid_stats`

## Key Data Structures

- `uihashtbl` is an SLIST hash table of `struct uidinfo`.
- `uihash` is the hash mask from `hashinit`.
- `UIHASH(uid)` selects the bucket by UID.
- Each `uidinfo` holds counts such as processes, LWPs, locks, semaphores, and socket buffer usage.

## Control Flow

- `uid_init` creates a larger hash on MP systems, ensures UID 0 exists for interrupt-context socket buffer accounting, installs sysctls, and registers hash stats.
- `uid_find` searches a bucket locklessly. If absent, it allocates a zeroed `uidinfo`, initializes `ui_uid`, and atomically inserts it with `atomic_cas_ptr`; races restart and free the unused allocation.
- `chgproccnt`, `chglwpcnt`, and `chgsemcnt` find the UID record and atomically adjust the relevant count, asserting it does not go negative.
- `chgsbsize` atomically adjusts socket buffer usage and rolls back if a positive change exceeds the supplied limit.
- Sysctl reads find the effective UID's `uidinfo` and expose selected counters as quad values.

## Concurrency And Invariants

- UID table insertion intentionally bypasses SLIST abstraction to make head insertion atomic.
- Readers use `membar_datadep_consumer` while traversing buckets.
- Resource counters are modified with atomic add operations.
- UID records are not removed, avoiding reclamation hazards for lockless readers.
- UID 0 must always be present after initialization.

## Risks And Edge Cases

- `chgsbsize` casts the counter through `long *`; correctness depends on field type/layout matching.
- Sysctl counter lookup uses offsets into `struct uidinfo`; field name and layout changes must keep the table synchronized.
- Hash table size is tuned to reduce MP cacheline writeback pressure from long chains.
