# File Research: sources/os/linux/linux/fs/fuse/cuse.c

## Purpose
This file implements CUSE, Character device in Userspace. It lets a userspace daemon open `/dev/cuse`, complete a FUSE-like initialization handshake, and register a real character device whose file operations are forwarded to the daemon via the FUSE request machinery.

## Main Definitions
- `struct cuse_conn` embeds a dummy `fuse_mount`, a `fuse_conn`, and the registered `cdev`/`device`.
- `cuse_conntbl[64]` maps character device numbers to active CUSE connections under `cuse_lock`.
- Frontend file ops (`cuse_frontend_fops`) implement read, write, open, release, ioctl, compat ioctl, poll, and no-op llseek.
- `cuse_parse_one()` and `cuse_parse_devinfo()` parse packed init reply key/value data, currently requiring `DEVNAME`.
- `cuse_process_init_reply()` validates daemon init response, parses device info, reserves device number, creates the device, creates and registers the cdev, links the connection, and sends uevents.
- `cuse_channel_open()` creates a new CUSE connection when `/dev/cuse` is opened.
- `cuse_channel_release()` removes the connection and registered device when the daemon channel closes.
- Sysfs attributes `waiting` and `abort` expose status/control per CUSE device.

## Control Flow And Behavior
The daemon opens `/dev/cuse`, which allocates `cuse_conn`, initializes its embedded FUSE connection, installs a FUSE device, marks it initialized, and sends an asynchronous `CUSE_INIT` request. The daemon replies with kernel ABI version, max read/write sizes, flags, device numbers, and packed device info. The reply handler registers the actual character device and makes it visible only after all registration is complete.

Opening the created character device looks up the connection by `dev_t`, takes a FUSE connection reference, and delegates open to `fuse_do_open()`. Reads and writes use `fuse_direct_io()` in CUSE mode, with writes intentionally leaving locking and checks to the server. Ioctls route to `fuse_do_ioctl()` and include unrestricted/compat flags as negotiated.

## Dependencies And Interfaces
CUSE depends on the FUSE core device path, miscdevice registration, char device APIs, device model/class APIs, sysfs attributes, and user namespace-aware FUSE connection initialization.

## Concurrency And Safety
`cuse_lock` protects registration, lookup, uniqueness checks, and removal from the connection table. The open path takes a FUSE connection reference so the connection remains alive while the character-device fd is active. Channel close removes the table entry first to stop new opens before unregistering device objects.

## Research Notes
CUSE is structurally a FUSE transport plus a char-device façade. Lifetime is daemon-channel driven: closing `/dev/cuse` removes the device and initiates FUSE device release.
