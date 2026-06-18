# File Research: sources/os/linux/linux/fs/coda/psdev.c

## Purpose
Implements Coda's pseudo-device character driver, module initialization, communication queues between the kernel and Venus, and sysctl/filesystem/device registration.

## Main Elements
- Global communication state: `coda_comms[MAX_CODADEVS]` stores per-device pending/processing queues, waitqueue, sequence counter, mount binding, and open state.
- Device operations: `coda_psdev_open()`, `release()`, `read()`, `write()`, `poll()`, and `ioctl()` implement the Venus communication ABI.
- Kernel-to-Venus request delivery: `coda_psdev_read()` waits for queued upcalls, copies request data to userspace, and moves synchronous requests to `vc_processing`.
- Venus-to-kernel replies/downcalls: `coda_psdev_write()` distinguishes downcalls from replies, dispatches invalidations via `coda_downcall()`, or matches replies by `unique` to wake sleeping upcall waiters.
- Open/release lifecycle: only one opener per pseudo-device is allowed; release aborts or frees pending and processing requests.
- Module setup: `init_coda()` creates the inode cache, registers the char device and class devices, initializes sysctls, and registers `coda_fs_type`.

## Dependencies And Integration
This file is the runtime transport for `upcall.c`. It owns the pseudo-device major `CODA_PSDEV_MAJOR`, exposes `/dev/cfsN` devices, and initializes Coda-wide sysctls from `sysctl.c` and filesystem registration from `inode.c`.

## Risk Notes
Queue state is protected by `vc_mutex`; request matching relies on unique IDs assigned in `coda_upcall()`. `CODA_OPEN_BY_FD` replies convert a Venus fd into a kernel `struct file *` via `fget()`, so bad fd handling is critical. Release races must wake synchronous waiters and free async requests without leaking request buffers.
