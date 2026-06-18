# File Research: sources/virtualization/spdk/module/bdev/nvme/vbdev_opal.c

This file implements OPAL locking-range virtual bdevs over NVMe bdevs. It registers the `opal` bdev module, creates SPDK partition bdevs for OPAL locking ranges, forwards I/O to the partition base, and uses SPDK OPAL commands to configure ranges, lock/unlock them, create users, query range state, and securely erase/reset ranges during deletion.

State is split between `opal_vbdev` entries and `vbdev_opal_part_base` entries. An `opal_vbdev` records name, NVMe controller, OPAL device, locking range ID, start/length, and constructed `spdk_bdev_part`. A part base groups all OPAL partitions over the same base NVMe bdev. Only NSID 1 is supported.

The bdev function table delegates I/O support to the base bdev and submits requests through `spdk_bdev_part_submit_request()`. Reads first request a buffer with `spdk_bdev_io_get_buf()`. If part submission returns `-ENOMEM`, the request is queued with `spdk_bdev_queue_io_wait()` and resubmitted later; other submission errors fail the I/O.

`vbdev_opal_create()` verifies the controller exists, has an OPAL device, and has namespace 1. It finds or constructs a partition base over the NVMe bdev, creates an OPAL vbdev name like `<base_bdev>r<range_id>`, programs the OPAL locking range using the admin password, constructs the SPDK partition bdev over the requested block range, and initially locks it with `OPAL_RWLOCK`.

`vbdev_opal_destruct()` looks up the OPAL vbdev, secure-erases its locking range, resets the range start/length to zero, frees cached locking range info, unregisters the partition bdev, and removes the config entry. `vbdev_opal_set_lock_state()` maps `READWRITE`, `READONLY`, and `RWLOCK` strings to OPAL lock states. `vbdev_opal_enable_new_user()` enables a user, sets the user password, and grants read-only and read-write access to the range.

Important invariants are NSID 1 only, range setup before partition construction, initial lock after successful partition construction, part-base hotremove cleanup, and careful lifetime around queued bdev I/O and partition/base objects.
