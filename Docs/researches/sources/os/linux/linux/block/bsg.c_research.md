# File Research: sources/os/linux/linux/block/bsg.c

## Scope

This file implements the block SCSI generic character device layer. It registers `/dev/bsg/<name>` devices, handles SG-compatible ioctls and io_uring passthrough dispatch, and links bsg devices from a disk queue sysfs directory.

## Core State and Entry Points

- `struct bsg_device` stores the backing request queue, embedded `device`, `cdev`, max command queue depth, default timeout, reserved buffer size, SG_IO callback, and io_uring callback.
- `bsg_register_queue()` allocates a minor, initializes the device/cdev, registers it with the `bsg` class, and creates a `queue/bsg` sysfs link when the queue has a disk kobject.
- `bsg_unregister_queue()` removes the sysfs link, deletes the cdev/device pair, and drops the device reference.
- File operations:
  - `bsg_open()` pins the request queue with `blk_get_queue()`.
  - `bsg_release()` drops that queue reference.
  - `bsg_ioctl()` implements SG queue depth, timeout, reserved-size, version, emulated-host, and `SG_IO` handling; unsupported old `SCSI_IOCTL_SEND_COMMAND` is rejected with a rate-limited warning.
  - `bsg_uring_cmd()` requires `IO_URING_F_SQE128 | IO_URING_F_CQE32` and delegates to the registered uring callback.
- `bsg_init()` registers the class and allocates the character device major during device init.

## Dependencies and Invariants

- Uses IDA for minor allocation and frees minors in `bsg_device_release()`.
- `bsg_timeout()` enforces at least `BLK_MIN_SG_TIMEOUT`, preferring per-command timeout, then device timeout, then the default SG timeout.
- `SG_IO` requires the user header guard `'Q'` before delegating to the queue-specific SG handler.
- The class devnode is `bsg/<device-name>`, producing the `/dev/bsg/...` namespace.
