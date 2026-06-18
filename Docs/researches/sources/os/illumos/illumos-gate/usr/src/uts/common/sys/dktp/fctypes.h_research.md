# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/fctypes.h

## Scope

Complete file read, 79 lines. This header defines shared data structures for DKTP flow-control implementations.

## Public Surface

It defines:

- Flow-control maximum outstanding counts `DMULT_MAXCNT` and `DUPLX_MAXCNT`.
- Field aliases for common data embedded in specific flow-control structures.
- `struct fc_data_cmn`: kstat pointer, mutex, and target common object pointer.
- `struct fc_data`: common state, flags, outstanding count, disk queue head, and queue object pointer.
- Disk queue aliases `ds_actf`, `ds_actl`, `ds_waitcnt`, and `ds_bp`.
- `struct fc_que`: queue chain entry with queue object, buffer, current outstanding count, and max count.
- `struct duplx_data`: duplex read and write queues plus common state.

## Behavior And Integration

Flow-control implementations use these structures to track outstanding I/O, queue buffers, and expose kstats while cooperating with queue objects and target common transport.

## Dependencies And Invariants

The header assumes `kstat_t`, `kmutex_t`, `opaque_t`, `struct diskhd`, and `struct buf` are available. Field aliases depend on exact embedded member names.

## Risks

The field-alias macros make refactoring hazardous. Queue counters are `short`, so implementations must honor the small maximum-count constants and not allow unbounded outstanding I/O.
