# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_ktr.c

## Purpose
Implements global state and the tracepoint write path for FreeBSD's low-level KTR kernel tracing facility.

## Key Interfaces
- Global exported state: `ktr_idx`, `ktr_mask`, `ktr_compile`, `ktr_entries`, `ktr_version`, `ktr_buf`, and `ktr_cpumask`.
- Sysctls under `debug.ktr`: `version`, `compile`, `cpumask`, `clear`, `mask`, `entries`, and optional ALQ controls.
- `ktr_tracepoint()` records a KTR event.
- DDB `show ktr` support dumps the circular trace buffer.

## State And Locking
KTR uses a circular array of `struct ktr_entry`. Writers reserve slots with atomic compare-and-set on `ktr_idx`. Runtime resizing disables tracing, quiesces CPUs, swaps buffers, and frees the old buffer. CPU filtering is controlled by `ktr_cpumask`.

## Control Flow
A tracepoint returns early during panic/debugger activity, disabled masks, null buffer, or filtered CPU. It prevents recursion with `TDP_INKTR` when verbose or ALQ logging is enabled. Events are written either to the in-memory ring or optional ALQ output. Each record stores timestamp, CPU, thread pointer, source file/line, format string, and up to six parameters.

## Integration Notes
Uses sysctl, cpuset parsing, `get_cyclecount()`, optional ALQ, optional DDB, and optional SMP CPU labeling. Boot-time `KTR_ENTRIES > KTR_BOOT_ENTRIES` migration preserves early entries.

## Risks
Trace records keep pointers to format strings and file strings rather than copying them. Sysctl buffer clearing and resizing are intentionally coarse and can race with concurrent tracing except for the quiesce/disable sequence in resizing.
