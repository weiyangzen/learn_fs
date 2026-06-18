# File Research: sources/virtualization/libblockdev/src/plugins/loop.c

## Purpose

`loop.c` implements libblockdev's loop-device plugin. It exposes GLib-style API wrappers around Linux loop ioctls, `/dev/loop-control`, `/dev/loopN`, and sysfs loop metadata so callers can create, inspect, resize, modify, and tear down loop devices.

All public operations use byte units and return `GError` details through the `BD_LOOP_ERROR` domain.

## Main Operations

- `bd_loop_init()` / `bd_loop_close()` are no-op plugin lifecycle hooks.
- `bd_loop_is_tech_avail()` reports all loop tech/mode combinations as supported by this implementation.
- `bd_loop_info()` opens a loop device, issues `LOOP_GET_STATUS64`, translates `lo_flags` into `BDLoopInfo`, and reads `/sys/class/block/<loop>/loop/backing_file`.
- `bd_loop_get_loop_name()` scans `/sys/block/loop*/loop/backing_file` and returns the loop device whose backing file exactly matches the requested path.
- `bd_loop_setup()` opens a file read-write, then delegates to `bd_loop_setup_from_fd()`.
- `bd_loop_setup_from_fd()` allocates a free loop device through `/dev/loop-control`, binds the provided fd with `LOOP_SET_FD`, applies status with `LOOP_SET_STATUS64`, optionally sets logical sector size with `LOOP_SET_BLOCK_SIZE`, and returns the loop name.
- `bd_loop_teardown()` detaches the backing file with `LOOP_CLR_FD`.
- `bd_loop_set_autoclear()` reads loop status, toggles `LO_FLAGS_AUTOCLEAR`, and writes status back.
- `bd_loop_set_capacity()` forces the loop driver to reread backing-file size using `LOOP_SET_CAPACITY`.

## Implementation Notes

`bd_loop_setup_from_fd()` serializes `LOOP_CTL_GET_FREE` with a static `GMutex` because concurrent access to `/dev/loop-control` is treated as unsafe in practice. Both status-setting and capacity-changing retry up to 10 times on `EAGAIN`, sleeping 100 ms between attempts.

The setup path deliberately opens the backing file `O_RDWR`; the requested loop read-only state is represented in loop flags and in how `/dev/loopN` is opened. If later status or block-size setup fails after `LOOP_SET_FD`, the code tries to clear the loop device with `LOOP_CLR_FD` and logs a warning if cleanup also fails.

## Data and Error Model

`BDLoopInfo` is owned by the caller and has explicit copy/free helpers. The implementation maps ENXIO from `LOOP_GET_STATUS64` to `BD_LOOP_ERROR_DEVICE`; most ioctl/open failures become `BD_LOOP_ERROR_FAIL` or `BD_LOOP_ERROR_DEVICE`.

Progress is reported through `bd_utils_report_started()`, `bd_utils_report_progress()`, and `bd_utils_report_finished()` for create, teardown, autoclear, and capacity operations.

## Dependencies and Integration

This file depends on Linux-specific loop kernel ABI headers and ioctls:

- `<linux/loop.h>`
- `LOOP_CTL_GET_FREE`
- `LOOP_SET_FD`
- `LOOP_SET_STATUS64`
- `LOOP_GET_STATUS64`
- `LOOP_CLR_FD`
- `LOOP_SET_CAPACITY`
- `LOOP_SET_BLOCK_SIZE`

It also integrates with libblockdev utility logging/progress helpers from `<blockdev/utils.h>`.

## Research Notes

The file is a Linux block-device integration layer rather than filesystem logic. Its filesystem relevance is enabling regular files to become block devices for filesystems, partition scanning, testing, virtualization images, and image-backed storage workflows.
