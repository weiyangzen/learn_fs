# File Research: sources/virtualization/spdk/module/bdev/iscsi/bdev_iscsi.c

## Purpose
Implements an SPDK bdev backed by a remote iSCSI LUN using libiscsi. It manages asynchronous connection setup, SCSI inquiry/capacity discovery, I/O translation, polling, timeout service, resize detection, and bdev lifecycle.

## Main Entry Points
- `create_iscsi_disk()` parses the iSCSI URL, creates a libiscsi context, starts async login, and queues a connection request.
- `delete_iscsi_disk()` unregisters an iSCSI bdev.
- `bdev_iscsi_get_opts()` and `bdev_iscsi_set_opts()` manage global timeout settings.
- `bdev_iscsi_submit_request()` routes bdev I/O to the owning iSCSI service thread.
- Module init/fini register config JSON behavior and clear outstanding connection requests.

## Internal Mechanics
Connection setup is a staged state machine driven by `iscsi_bdev_conn_poll()`: async connect, logical block provisioning inquiry, optional block limits inquiry, READ CAPACITY(16), then `create_iscsi_lun()`. Successful creation registers an SPDK bdev with geometry from READ CAPACITY and UNMAP capabilities from inquiry pages.

The first I/O channel establishes `lun->main_td` and starts pollers for libiscsi fd service and timeout checks. Later I/O submitted from other SPDK threads is sent to `main_td`; completion is sent back to the original submitting thread if needed. A no-main-channel poller keeps servicing the libiscsi context while no regular I/O channel exists.

READ maps to READ(16), WRITE to WRITE(16), FLUSH to SYNCHRONIZE CACHE(16), UNMAP to SCSI UNMAP with at most one descriptor, and RESET to an async LUN reset task management function. Command callbacks complete with SCSI status and sense data. Unit attention for capacity change triggers READ CAPACITY(16), notifies block-count growth if larger, and retries the failed I/O.

## Dependencies
Uses SPDK bdev/thread/fd/env/JSON/string utilities, libiscsi (`iscsi/iscsi.h`, `iscsi/scsi-lowlevel.h`), POSIX poll, pthread mutexes, and SCSI/iSCSI protocol constants.

## Risks and Notes
Thread affinity is central: libiscsi service and request submission are serialized on `main_td`, with mutex-protected channel-count transitions. `bdev_iscsi_resize()` only accepts growth, not shrink. UNMAP supports only one descriptor, so requests larger than `max_unmap` are rejected despite splitting calculations. Connection request cleanup is delayed until after `iscsi_service()` unwinds, using `req->status` as a lifecycle marker.
