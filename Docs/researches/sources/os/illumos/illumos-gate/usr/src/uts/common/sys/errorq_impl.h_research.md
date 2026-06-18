# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/errorq_impl.h

## Role

`errorq_impl.h` is the private implementation header for `errorq`. It expands the opaque public types with queue element, nvlist element, kstat, and queue state layouts.

## Data Structures

- `errorq_nvelem_t` binds an nvlist element to its fixed buffer and `nv_alloc_t`.
- `struct errorq_elem` contains links for processing/free/pending lists, crash-dump list linkage, and the element payload pointer.
- `errorq_kstat_t` tracks dispatched, dropped, logged, reserved, reservation failures, committed, commit failures, and cancelled counts.
- Defines implementation flags `ERRORQ_ACTIVE` and `ERRORQ_NVLIST`, deliberately in the private bit range 16-31.
- Defines `ERRORQ_NAMELEN` as 31.
- `struct errorq` contains the queue name, kstats and installed kstat pointer, drain callback/private data, backing data buffer, queue length and element size, soft interrupt priority and id, flags, consumer lock, element array, processing head/tail, pending list, free bitmap, crash-dump list, global list linkage, and bitmap rotor.

## Contract Notes

This file must agree with `errorq.h` opaque type declarations. Its list and bitmap fields describe a fixed-size queue with both normal dispatch and crash-dump retention paths.
