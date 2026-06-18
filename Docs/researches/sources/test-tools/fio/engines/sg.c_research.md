# sources/test-tools/fio/engines/sg.c

## Purpose
`sg.c` implements fio's Linux SCSI generic ioengine. It builds SCSI CDBs for read, write, write-and-verify, write-same, verify, write-stream, unmap/TRIM, and sync-cache commands, then executes them through either block-device `SG_IO` ioctl or sg character-device read/write command queues.

## Important APIs, Types, And Functions
`struct sg_options` exposes high-priority polling, FUA flags, write mode, and stream ID. `struct sgio_cmd` stores a 16-byte CDB plus sense buffer per depth slot. `struct sgio_trim` batches multiple fio TRIM `io_u`s into one UNMAP command. `struct sgio_data` owns command storage, event array, pollfd array, saved fd flags, read buffer, block size, type-check state, and trim queues.

Core helpers are endian setters/getters, `sgio_hdr_init()`, `fio_sgio_rw_lba()`, `fio_sgio_prep()`, `fio_sgio_unmap_setup()`, `fio_sgio_doio()`, `fio_sgio_getevents()`, `fio_sgio_commit()`, `fio_sgio_read_capacity()`, `fio_sgio_type_check()`, stream open/close helpers, and `fio_sgio_errdetails()`.

## Control Flow
`.init` allocates per-depth command, event, sg header, and TRIM batching structures, then forces `override_sync`. `.open_file` uses `generic_open_file`, performs one-time type/block-size detection, and opens a stream when requested. `.prep` translates fio direction, offset, and transfer length into an SG header and CDB. `.queue` decides synchronous versus async operation based on direct/sync settings and direction. Block devices use `ioctl(SG_IO)` synchronously. Character devices use write/read of `sg_io_hdr`, asynchronously unless direct/sync/sync-command mode forces immediate readback. Async TRIM ranges are batched and submitted in `.commit`; `.getevents` polls sg fds and expands one UNMAP completion back to all batched fio `io_u`s.

## State And Persistence
The engine mutates target SCSI devices directly. Stream IDs may be opened and closed around a job. Async state is held in `trim_queues`, `events`, and sg driver queues. For block devices, `.type_check` disables `.getevents`, `.event`, and `.commit` because all I/O completes synchronously through ioctl.

## Dependencies And Integration Points
The implementation depends on Linux SG interfaces (`sg_io_hdr`, `SG_IO`, `SG_GET_VERSION_NUM`), block ioctls, fio raw I/O flags, generic file open/close, fio error-detail hooks, and fio's special accounting functions for engines that sometimes complete synchronously inside `.queue`.

## Risks
The engine has high device risk: malformed CDBs or wrong options can modify real SCSI media. Mixed `/dev/sdX` and `/dev/sgY` jobs are called out as problematic because type checking mutates global engine hooks after the first file. Async TRIM batching depends on `current_queue` and per-index maps; incorrect queue accounting would misattribute completions. `fio_sgio_getevents()` restores nonblocking flags only in the `min == 0` path. Error-detail strings are allocated and must be freed by the caller.

## Test Signals
Tests should cover block-device sync mode, sg-character async mode, all write modes' CDB bytes, 10-byte versus 16-byte LBA transitions, UNMAP batching, stream open/close, error-detail formatting from synthetic headers, and builds without `FIO_HAVE_SGIO`. Integration should run only against disposable SCSI targets or emulators.
