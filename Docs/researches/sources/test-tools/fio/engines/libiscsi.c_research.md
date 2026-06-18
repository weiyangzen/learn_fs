# sources/test-tools/fio/engines/libiscsi.c

## Purpose
Implements an iSCSI fio engine using libiscsi and SCSI CDB helpers. It connects each fio file URL as a LUN, discovers capacity and block size, submits asynchronous SCSI READ16/WRITE16/SYNCHRONIZE CACHE commands, and polls libiscsi file descriptors for completions.

## Important APIs, Types, And Functions
`struct iscsi_lun` owns a libiscsi context, parsed URL, block size, and block count. `struct iscsi_info` owns all LUNs, pollfd array, completed-event list, and event count. `struct iscsi_task` links a SCSI task to its LUN and fio `io_u`. Important functions are `fio_iscsi_setup_lun()`, `fio_iscsi_setup()`, `fio_iscsi_queue()`, `iscsi_cb()`, `fio_iscsi_getevents()`, `fio_iscsi_event()`, and cleanup helpers.

## Control Flow
Setup parses each file name as a full iSCSI URL, creates a context using the configured initiator, sets target/session/header-digest options, connects synchronously, sends READ CAPACITY(16), extracts block size and block count, stores real fio size, and records the libiscsi fd in `pfds`. Queue validates read/write alignment to the LUN block size, builds READ16/WRITE16 or synchronize-cache CDBs, attaches buffers, allocates an `iscsi_task`, and submits asynchronously. The callback records success or error and appends the task to `complete_events`. `getevents` polls all LUN fds, services libiscsi events until at least `min` completions are buffered, and `event` frees the SCSI task wrapper.

## State And Persistence
Each fio file's `engine_data` points to its LUN. Completion state is buffered in `iscsi_info->complete_events` until fio consumes it. Persistent effects are remote SCSI writes and cache synchronize commands.

## Dependencies And Integration Points
Depends on libiscsi, SCSI low-level helpers, `poll()`, and fio diskless async event hooks. It bypasses generic file open/close and registers no-op open/close.

## Risks
Setup allocations are not fully checked for NULL. The loop in `fio_iscsi_setup()` breaks only on `ret < 0`, while some setup errors are positive, which can leave partially initialized state. `complete_events` is sized by `iodepth` and callback increments without explicit bounds. Sync command length uses bytes where SCSI synchronize-cache expects block addressing fields from the helper API. Poll timeout ignores fio's `timespec` parameter.

## Test Signals
Test valid and invalid iSCSI URLs, multiple LUNs, capacity discovery, unaligned offset/buffer rejection, read/write/sync command completion, failed SCSI statuses, partial setup cleanup, concurrent completions up to `iodepth`, EINTR/EAGAIN poll handling, and logout/destroy cleanup.
