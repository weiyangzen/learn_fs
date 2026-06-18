# sources/sync-backup/casync/src/canbd.c

## Purpose
`canbd.c` exposes a read-only Linux Network Block Device backed by data supplied from casync. It opens or finds `/dev/nbdN`, configures NBD ioctls, receives kernel read requests over a socketpair, and sends replies with caller-provided data.

## Important APIs, Types, and Functions
`struct CaBlockDevice` tracks the NBD device fd, socketpair, selected device path, helper ioctl process, last NBD request, exported size, friendly-name state, and device number. `ca_block_device_set_size()` enforces a positive 512-byte-aligned size. `ca_block_device_open()` opens a configured path or scans `/dev/nbd0` through `/dev/nbd1023`, attaches the socket with `NBD_SET_SOCK`, sets read-only block size and size, and forks a child blocked in `NBD_DO_IT`. `ca_block_device_step()` reads and validates one `struct nbd_request`. `ca_block_device_get_request_offset()`, `ca_block_device_get_request_size()`, and `ca_block_device_put_data()` implement request/response exchange. Friendly-name helpers create locked files under `/run/casync` for udev/tooling integration.

## Control Flow
The caller creates the object, sets size and optionally path/friendly name, then opens the device. After open, the caller polls `ca_block_device_get_poll_fd()` or `ca_block_device_poll()`, calls `ca_block_device_step()` until a request is available, fetches offset and size, reads bytes from the casync index/archive machinery, and completes the kernel request via `ca_block_device_put_data()`. Unref disconnects the NBD socket, clears it, kills the ioctl child, removes friendly-name files, and closes descriptors.

## State and Persistence
Runtime state is fd-heavy and process-backed. Persistent-ish side effects include `/run/casync/<device>` friendly-name files guarded by BSD locks. The object also mutates kernel NBD state and a block device read-only flag. No exported data is persisted by this module.

## Dependencies and Integration Points
This is Linux-specific, using `<linux/nbd.h>`, `<linux/fs.h>`, `ioctl()`, `socketpair()`, `poll()`, `flock()`, and `/dev/nbd*`. `casync-tool.c` includes `canbd.h`, and `test/test-nbd.sh.in` exercises `casync mkdev` against `/dev/nbd0` when root and NBD support are available.

## Risks
NBD setup requires privileges and loaded kernel support. Failure cleanup must keep kernel NBD devices from staying attached; the unref path is therefore critical. `ca_block_device_poll()` returns `1` even on timeout instead of the raw `ppoll()` result, so callers must still call `step()` to distinguish readiness. Friendly-name creation races are mitigated with locks and rename-noreplace, but failures can leave stale files if the process is killed at unfortunate points.

## Test Signals
`test/test-nbd.sh.in` covers an end-to-end mkdev readback digest when run as root with `/dev/nbd0`. Unit tests for invalid request headers, unaligned sizes, friendly-name replacement, and timeout behavior would strengthen coverage.
