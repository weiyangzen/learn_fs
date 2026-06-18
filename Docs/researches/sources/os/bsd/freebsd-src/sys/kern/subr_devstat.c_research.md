# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_devstat.c

## Purpose
Implements kernel device I/O statistics used by storage devices and exposed to userland through `kern.devstat.*` sysctls and the `devstat` mmap device.

## Key Elements
- Global list: `device_statq`.
- Synchronization: `devstat_mutex`.
- Public lifecycle: `devstat_new_entry()`, `devstat_remove_entry()`.
- Transaction accounting: `devstat_start_transaction*()`, `devstat_end_transaction*()`.
- BIO integration: `devstat_start_transaction_bio*()`, `devstat_end_transaction_bio*()`.
- Sysctls: `kern.devstat.all`, `numdevs`, `generation`, `version`.
- mmap backing allocator: `struct statspage`, `devstat_alloc()`, `devstat_free()`.
- DTrace SDT probes: `io:start` and `io:done`.

## Behavior
Devices are inserted into a priority-sorted STAILQ, then assigned monotonically increasing device numbers and creation times. Transaction starts and completions update counters mostly locklessly, using `sequence0` and `sequence1` as consistency markers for mmap readers.

`devstat_end_transaction()` updates bytes, operation counts, tag counts, duration, busy time, and end counts. BIO wrappers derive read/write/free/no-data categories from `bio_cmd`, account residual bytes, and emit DTrace probes.

The `kern.devstat.all` sysctl emits a generation number followed by each `struct devstat`, retrying with `EBUSY` if the list changes during traversal. The mmap path exposes pages of allocated `struct devstat` entries read-only.

## Research Notes
The sequence fields are deliberately placed and updated to let lockless userland snapshots detect torn reads. Structural list changes are mutex-protected; per-device counters rely on ordered atomic sequence updates.
