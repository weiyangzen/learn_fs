# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_ktr.c

## Purpose

`kern_ktr.c` implements the in-kernel KTR tracepoint facility: per-CPU ring buffers of low-overhead trace events used during boot, runtime diagnostics, optional timing tests, and DDB inspection.

## Main Responsibilities

- Defines boot and runtime KTR ring buffer sizing.
- Provides early boot trace storage for CPU 0 and migrates it after normal allocation is available.
- Allocates per-CPU trace buffers in `ktr_sysinit()`.
- Provides `ktr_begin_write_entry()` and `ktr_finish_write_entry()` for tracepoint writes.
- Optionally resynchronizes TSC offsets across CPUs through a periodic callout.
- Provides optional test logging, IPI ping-pong, critical-section, and spinlock overhead probes.
- Provides `show ktr` DDB output sorted by timestamp across CPUs.

## Core Data Model

`ktr_cpu[MAXCPU]` holds each CPU's `ktr_cpu_core`, including a trace buffer and monotonically increasing index. Writers use `ktr_idx & ktr_entries_mask` to select the next slot. Each `struct ktr_entry` records timestamp, tracepoint metadata, source file, source line, and optional caller stack information.

During early boot CPU 0 writes to `ktr_buf0`; `ktr_sysinit()` allocates full-size buffers for all CPUs and copies early CPU 0 entries into the new buffer. The exposed `debug.ktr.entries`, `debug.ktr.version`, `debug.ktr.stacktrace`, and test sysctls describe runtime state.

## Timestamp and Resync Behavior

If the architecture supports TSC, entries use `rdtsc() - tsc_offsets[cpu]`; otherwise they use approximate wall time. When `debug.ktr.resynchronize` is enabled, CPU 0 periodically uses an LWKT CPU sync callback to update per-CPU TSC offsets. The code deliberately uses a callout rather than a preemptive systimer to reduce the risk of deadlock while CPUs hold spinlocks or serializers.

## DDB Integration

The `show ktr` command supports verbose output, all-output mode, and per-CPU filtering. It walks each CPU's ring backwards and prints entries in decreasing timestamp order. The output includes CPU, ring index, optional timestamp/source location, tracepoint name, and caller addresses.
