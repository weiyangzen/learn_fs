# sources/test-tools/liburing/test/uring_cmd_ublk.c

Purpose: end-to-end test of cancellable `IORING_OP_URING_CMD` through the Linux ublk userspace block driver. It creates a null ublk device, runs direct fixed-buffer I/O against it, kills the userspace daemon mid-I/O, and checks that uring command cancellation and device teardown complete.

Important APIs/types/functions: when `CONFIG_HAVE_UBLK_HEADER` is present, key types include `struct ublk_dev`, `struct ublk_queue`, `struct ublk_io`, `struct ublk_tgt_ops`, and `struct io_ctx`. Control functions include `ublk_ctrl_init_cmd`, `__ublk_ctrl_cmd`, `ublk_ctrl_{add,del,get_info,set_params,get_features,start_dev}`, `ublk_queue_init`, `ublk_queue_io_cmd`, `ublk_handle_cqe`, `ublk_process_io`, `ublk_io_handler_fn`, `cmd_dev_add`, `cmd_dev_del_by_kill`, `ublk_null_tgt_init`, `ublk_null_queue_io`, `__test_io`, `test_io_worker`, and `test_del_ublk_with_io`.

Control flow: main skips without ublk headers/device/features, then loops four times. Each loop adds a `null` ublk target with two queues and 128-depth queues. A forked daemon maps ublk command buffers, registers the char device fd as fixed file, submits fetch/commit uring commands for all tags, and completes null target I/O immediately by reporting byte counts. Parent waits for `/dev/ublkbN`, forks I/O workers doing fixed-buffer direct reads and writes over the block device, sleeps briefly, kills the daemon with SIGKILL, waits for `/dev/ublkcN` close notification, deletes the device, and verifies `GET_DEV_INFO` no longer succeeds.

State/persistence behavior: creates transient `/dev/ublkcN` and `/dev/ublkbN` kernel devices, daemon process state, per-queue mmaped command buffers, registered files, and aligned per-I/O buffers. The null target declares a 250 GiB device but does not persist backing data.

Dependencies/integration: requires kernel ublk support, `/dev/ublk-control`, ublk headers, `UBLK_F_CMD_IOCTL_ENCODE`, direct I/O, inotify on `/dev`, block device ioctls, pthreads, fork/daemon behavior, and io_uring SQE128 uring commands.

Risks/test signals: high privilege and kernel-feature sensitivity. It is skipped when ublk is unavailable. Failures include inability to add/start/delete devices, queue mmap/register failures, fixed I/O CQE length mismatch, daemon not closing, or device info still present after deletion. The target lookup loop is intended to scan `tgt_ops_list`, so any future list changes should review loop bounds carefully.
