# File Research: sources/os/bsd/netbsd-src/sys/sys/percpu_types.h

## Purpose
Provides forward declarations and basic data types for per-CPU storage without exposing full implementation.

## Main API
- Forward declaration: `struct cpu_info`.
- Opaque type: `percpu_t`.
- Per-CPU backing descriptor: `percpu_cpu_t` with size and data pointer.

## Dependencies
Includes `sys/types.h`.

## Risks and Notes
This header is deliberately small to break include cycles. It does not provide allocation or synchronization semantics; those are in `percpu.h`.
