# File Research: sources/virtualization/spdk/lib/nvme/nvme_cuse.c

This file exposes SPDK NVMe controllers and namespaces as Linux CUSE character devices compatible with common NVMe ioctls. It owns CUSE device objects, a detached FUSE polling thread, ioctl dispatch, passthrough command marshalling, namespace read/write ioctl support, namespace device creation/removal, controller index claiming, and public CUSE registration APIs.

`struct cuse_device` represents a controller or namespace CUSE node. Controller devices have `nsid == 0` and own a tailq of namespace devices. Namespace devices point back to their controller device. The global state includes a controller-device list, a bit array of claimed controller indexes, a pending-device queue, an active-device queue, an fd group, and an eventfd used to notify the CUSE thread of new sessions.

Passthrough ioctl handling maps Linux `struct nvme_passthru_cmd` into `struct spdk_nvme_cmd`. `cuse_nvme_passthru_cmd()` uses libfuse ioctl retry iovecs to make user buffers accessible, limits aggregate request size to `FUSE_MAX_SIZE`, rejects bidirectional transfers, copies host-to-controller payloads into DMA buffers, and queues execution through `nvme_io_msg_send()`. Execution runs on the controller’s external I/O message qpair: admin ioctl commands go through `spdk_nvme_ctrlr_cmd_admin_raw()`, while namespace I/O passthrough uses `spdk_nvme_ctrlr_cmd_io_raw_with_md()`.

Reset and rescan ioctls are controller-only. Reset queues either `spdk_nvme_ctrlr_reset()` or `spdk_nvme_ctrlr_reset_subsystem()` through the I/O message bridge. Rescan iterates active namespaces and calls `nvme_ns_identify()` without failing the ioctl if a namespace identify fails.

`NVME_IOCTL_SUBMIT_IO` on namespace devices supports read and write opcodes. The file uses the namespace sector size and metadata size to build retry iovecs, allocates DMA data and optional metadata buffers, then submits `spdk_nvme_ns_cmd_read_with_md()` or `spdk_nvme_ns_cmd_write_with_md()` through the external qpair. Completion callbacks translate NVMe completion status into the FUSE ioctl result and return read data/metadata when needed.

Other namespace ioctls include `NVME_IOCTL_ID`, `BLKPBSZGET`, `BLKSSZGET`, `BLKGETSIZE`, and `BLKGETSIZE64`. As read, `BLKGETSIZE64` replies with `spdk_nvme_ns_get_num_sectors(ns)` rather than a byte count; that is worth checking before relying on block-device-size compatibility.

CUSE session creation uses `cuse_lowlevel_setup()` with unrestricted ioctl support and per-device low-level ops. The CUSE thread polls the SPDK fd group, receives FUSE buffers, processes sessions, handles session exit, and frees devices only after `force_exit` sessions are torn down. New sessions are added by queueing them on `g_pending_device_head` and writing the eventfd.

Controller device startup claims a stable `spdk/nvme<N>` name by locking `/var/tmp/spdk_nvme_cuse_lock_<N>` with `fcntl()`, recording the owner pid in an mmap’d int, setting the started bit, creating the controller CUSE session, and creating namespace sessions for all active namespaces. Namespace updates remove disappeared namespace devices and add newly active namespaces.

Public APIs are `spdk_nvme_cuse_register()`, `spdk_nvme_cuse_unregister()`, `spdk_nvme_cuse_update_namespaces()`, `spdk_nvme_cuse_get_ctrlr_name()`, and `spdk_nvme_cuse_get_ns_name()`. Registration is primary-process-only, registers the CUSE producer with `nvme_io_msg_ctrlr_register()`, starts the CUSE thread if needed, and starts the controller device. Unregister stops devices and unregisters the I/O message producer.

Key risks are asynchronous lifetime and lock ordering: FUSE requests own `cuse_io_ctx` until NVMe completion, CUSE devices are removed from logical lists before the CUSE thread frees them, and producer stop/update callbacks interact with both controller locks and `g_cuse_mtx`. The ioctl retry paths also depend on correct iovec sizing to prevent oversized FUSE requests.
