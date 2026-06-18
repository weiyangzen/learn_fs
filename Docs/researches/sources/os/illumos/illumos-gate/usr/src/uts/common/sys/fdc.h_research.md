# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fdc.h

## Purpose

`fdc.h` defines private floppy disk controller and floppy unit state for the illumos floppy driver. It covers minor-number layout, media format IDs, controller/unit state machines, DMA command state, drive open tracking, and controller operation vectors.

## Main Types

`xlate_tbl_t` maps integer values to encoded controller bytes.

`struct fdattr` stores floppy media rotational speed, interleave, and format/read gap lengths.

`struct fdisk` is per-drive media state: controller object, media capabilities, I/O statistics, sector size shift, open/close semaphore, active `buf_t` queue, partition map, regular/layered/exclusive open state, current/default floppy format, controller encoding values, media-change timeout/state, eject flag, media state condition variable, and VTOC label data.

`struct fdstat` counts operations and errors.

`struct fdcsb` is the controller command/status block, including DMA handles/cookies/windows, execution state, selected drive, command/result bytes, retry counters, status, and operation flags.

`struct fdcntlr` is per-controller state: locks, I/O condition variable, selection semaphore, suspend state, device info, register/DMA/interrupt configuration, chip/mode/flags, kstats, current unit, watchdog timer, per-unit objects, motor timers/state, current cylinders, seek direction, active command block, and cached hardware register values.

`struct fcobjops` is the floppy controller operation vector.

`struct fcu_obj` is a floppy unit object with flags, lock, driver-private data, drive/media attributes, device info, unit number, operation vector, and parent controller.

## Interfaces and Constants

Minor numbers encode partition in low 3 bits and drive instance above that. Macros include `PARTITION()`, `DRIVE()`, `FDUNIT()`, and `FDCTLR()`.

Format IDs include 5.25-inch and 3.5-inch formats such as `FMT_5H`, `FMT_3H`, `FMT_3E`, and `FMT_AUTO`.

Command execution states are enumerated in `enum fxstate`; motor states and inputs are in `enum fmtrstate` and `enum fmtrinput`.

Controller flags include `FCFLG_BUSY`, `FCFLG_WANT`, `FCFLG_WAITMR`, `FCFLG_WAITING`, `FCFLG_TIMEOUT`, `FCFLG_DSOUT`, and `FCFLG_3DMODE`.

Unit flags include drive-present, write-protect, characteristics-known, label-known, changed/ejected detection, 3D mode, and busy bits.

## Research Notes

This is driver-private block-device infrastructure for legacy floppy media. It matters to filesystem research because PCFS and removable-media paths can issue floppy ioctls and depend on media geometry, partition maps, label state, and media-change semantics.
