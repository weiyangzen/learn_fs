# File Research: sources/os/bsd/netbsd-src/sys/sys/evcnt.h

Read completely: 157 lines.

## Purpose
Declares NetBSD event counters: lightweight named counters used by kernel subsystems and exposed for diagnostics.

## Main Interfaces
- `struct evcnt`: 64-bit count, list linkage, type, group/name lengths, optional parent, group/name strings.
- Counter types: `EVCNT_TYPE_MISC`, `EVCNT_TYPE_INTR`, `EVCNT_TYPE_TRAP`, `EVCNT_TYPE_ANY`.
- Static counter macros: `EVCNT_INITIALIZER`, `EVCNT_ATTACH_STATIC`, `EVCNT_ATTACH_STATIC2`.
- Kernel routines: `evcnt_init`, `evcnt_attach_static`, `evcnt_attach_dynamic`, `evcnt_attach_dynamic_nozero`, `evcnt_detach`.
- `ev_count32` selects the right 32-bit half by endian order.

## Dependencies And Integration
Uses `sys/queue.h` and `sys/stdint.h`; kernel users link counters into `allevents`. Interrupt, trap, storage, and filesystem/device paths can use it for counters.

## Risks And Edge Cases
- Group/name strings are length-limited by `EVCNT_STRING_MAX`.
- 32-bit counter access depends on `_BYTE_ORDER`.
- Static attach relies on link sets.

## Filesystem Relevance
Moderate. Not filesystem-specific, but useful for filesystem, block, and device instrumentation.
