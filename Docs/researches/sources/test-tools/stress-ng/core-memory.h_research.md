# sources/test-tools/stress-ng/core-memory.h

## Purpose

This header declares memory information, accounting, and VM helper functions.

## Important APIs, Types, And Functions

It exposes page-size, memory/swap info, memory limit info, free-memory string, KSM, low-memory check, physical size, usage logging, address alignment, anonymous VMA naming, swapoff, readability, per-PID memory usage, and compaction APIs.

## Control Flow

Callers use these helpers to size stress workloads, avoid OOM, label mappings, and invoke optional kernel VM maintenance.

## State And Persistence Behavior

The implementation uses static caches and may mutate kernel VM controls. The header owns no state.

## Dependencies And Integration Points

It includes `stress-ng.h` for project types and is consumed by filesystem, mmap, shared-memory, and stressor code.

## Risks And Test Signals

The include guard is named `CORE_MEMORY_H_H`; changing it could affect duplicate-include behavior. Tests should compile broad consumers and validate no-op behavior for unsupported VM APIs.
