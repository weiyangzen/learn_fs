# sources/test-tools/stress-ng/core-interrupts.c

## Purpose

This file records and reports selected hardware/kernel interrupt counters before and after stressor execution. It detects failure-indicating interrupts such as machine checks, deferred APIC errors, IO-APIC errors, miscounts, and ARM unhandled interrupt errors, and it can summarize TLB shootdown/IPI activity from `/proc/interrupts`.

## Important APIs, Types, And Functions

`stress_interrupt_info_t` maps interrupt label strings to failure policy, logging function, and description. Public APIs are `stress_interrupts_start`, `stress_interrupts_stop`, `stress_interrupts_check_failure`, `stress_interrupts_dump`, and `stress_interrupts_tlb`. Internal helpers include `stress_interrupts_counter_set`, `stress_interrupts_count`, `stress_interrupt_tolower`, and Linux-only `stress_interrupts_parse_field`.

## Control Flow

Start and stop both call `stress_interrupts_count` with different slots. On x86, SMI count may be read from `MSR_SMI_COUNT` for the current CPU. The module then parses `/proc/interrupts`, finds known labels, sums per-CPU numeric columns, and stores start or stop counters. Failure checking compares deltas for entries marked `check_failure` and sets the caller's return code to `EXIT_FAILURE` when deltas are positive. Dumping walks stressor list items, averages positive deltas across instances, logs via the interrupt-specific logging function, and emits YAML keys derived from descriptions.

## State And Persistence Behavior

Counter state is stored in caller-provided `stress_interrupts_t` arrays, typically per stressor instance. The module has a static interrupt metadata table but no mutable global state. It reads kernel counters and does not reset them.

## Dependencies And Integration Points

It depends on architecture detection, x86 MSR reads from `core-helper.c`, stressor list/stat types, logging/YAML output, and Linux `/proc/interrupts`. `STRESS_INTERRUPTS_MAX` must be large enough for the metadata table.

## Risks And Test Signals

Parsing `/proc/interrupts` is format-sensitive and architecture-dependent. Counter wrap or CPU hotplug can affect deltas. Failure policy can produce false positives on hosts with pre-existing hardware issues. Test signals include correct summing of synthetic interrupt lines, no crash with missing `/proc/interrupts`, x86 MSR failure fallback, YAML output only when deltas exist, and failure return changes only for configured failure labels.
