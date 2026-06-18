# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/dadk.h

## Scope

Complete file read, 141 lines. This header defines the direct-access disk target implementation state and function prototypes for the `dadk` target disk object.

## Public Surface

It includes `sys/dktp/tgcom.h` and defines:

- `struct dadk`: target disk state including backpointers, logical/physical geometry, removable/read-only/CD-ROM/cache flags, sector/block shifts, BBH/flow/controller objects, embedded `tgcom_obj`, media state, synchronization, watcher-thread count, kstats, and command-count lock.
- `DAD_SECSIZ` alias to physical sector size.
- Timing/retry constants `DADK_BSY_TIMEOUT`, `DADK_IO_TIME`, `DADK_FLUSH_CACHE_TIME`, `DADK_RETRY_COUNT`, and `DADK_SILENT`.
- `PKT2DADK(pktp)`.
- Packet action codes `COMMAND_DONE`, `COMMAND_DONE_ERROR`, `QUE_COMMAND`, `QUE_SENSE`, and `JUST_RETURN`.
- `dadk_errstats_t` kstat layout.
- Prototypes for init/free/probe/attach/open/close/ioctl/strategy/geometry/I/O-buffer/dump/media/inquiry/cleanup and command-count routines.

## Behavior And Integration

`dadk` implements the `tgdk_objops` target disk contract declared in `tgdk.h`. It bridges SCSI direct-access devices to common disk operations, manages removable media state, coordinates with flow-control and controller objects, and exposes disk error statistics.

## Dependencies And Invariants

It depends on SCSI, DKIO media state, `tgdk_geom`, `tgdk_iob`, kstat, mutex/condition variable, and `struct buf` types from surrounding kernel headers. Media state and watcher thread counters are protected by `dad_mutex`/`dad_state_cv`; command count is protected by `dad_cmd_mutex`.

## Risks

The header declares `static void dadk_watch_thread(struct dadk *dadkp);`; a `static` prototype in a header gives each including translation unit an internal declaration and is only safe if used consistently with implementation visibility. Bitfields encode device attributes compactly but are not ABI-stable across compilers if serialized.
