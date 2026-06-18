# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_tslog.c

## Purpose
Implements a simple timestamp logging facility for boot/kernel events and selected userland process lifecycle events, exported through hidden debug sysctls.

## Key Interfaces
- `tslog()` records a timestamped kernel event with thread pointer, event type, facility string, and optional string.
- `debug.tslog` sysctl dumps loader-provided TSLOG data followed by in-kernel records.
- `tslog_user()` records fork, exec, first namei, and exit timestamps by PID.
- `debug.tslog_user` sysctl dumps per-PID user event data.
- `sysinit_tslog_shim()` wraps SYSINIT functions with enter/exit timestamp records.

## State And Locking
Kernel event records are stored in a fixed `timestamps[TSLOGSIZE]` array, with `nrecs` advanced atomically. User process records live in a `procs[PID_MAX + 1]` array and contain parent PID, fork/exit cycle counts, allocated exec/namei strings, and a reuse flag. There is no general lock around user process metadata.

## Control Flow
`tslog()` obtains `get_cyclecount()`, substitutes `thread0` for a null thread during early boot, reserves a slot with `atomic_fetchadd_long()`, and writes it if the fixed buffer has not overflowed. The sysctl handler builds an `sbuf`, prepends loader TSLOG data if present, and formats all recorded kernel entries. `tslog_user()` treats non-`-1` `ppid` as fork, non-null `execname` as exec update, non-null `namei` as first path capture, and otherwise records exit.

## Integration Notes
Used for low-overhead boot and event tracing. It depends on loader preload metadata, `sbuf`, `get_cyclecount()`, atomic operations, PID limits, and SYSINIT shim descriptors.

## Risks
The `debug.tslog` reader explicitly races with record writers and can theoretically observe a partially written record. The user process table is keyed directly by PID and marks entries reused when a fork for an already-used PID is seen; after reuse, later events for that PID are ignored. Dynamically allocated exec/namei strings are retained for the lifetime of the table.
