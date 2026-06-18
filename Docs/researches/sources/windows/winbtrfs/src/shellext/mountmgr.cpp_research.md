# File Research: sources/windows/winbtrfs/src/shellext/mountmgr.cpp

Read status: complete, 176 lines.

This file implements a small NT mount manager wrapper.

Key behavior:
- Constructor opens `MOUNTMGR_DEVICE_NAME` with `NtOpenFile` for generic read/write.
- Destructor closes the NT handle with `NtClose`.
- `create_point` builds `MOUNTMGR_CREATE_POINT_INPUT` and sends `IOCTL_MOUNTMGR_CREATE_POINT`.
- `delete_points` builds a `MOUNTMGR_MOUNT_POINT` filter from optional symlink, unique ID, and device name, then sends `IOCTL_MOUNTMGR_DELETE_POINTS`. It retries with the returned output size on `STATUS_BUFFER_OVERFLOW`.
- `query_points` builds the same filter structure and sends `IOCTL_MOUNTMGR_QUERY_POINTS`, resizes to the returned `MOUNTMGR_MOUNT_POINTS::Size`, retries, and converts results to `mountmgr_point` objects.

Integration:
- Used by `devices.cpp` to associate volumes/devices with DOS drive letters.
- Depends on shared `ntstatus_error` from shell extension support.

Risk and maintenance notes:
- `delete_points` and `query_points` duplicate filter-buffer construction logic.
- Offsets and lengths are manually calculated in bytes. Any future addition of fields should preserve Windows structure alignment expectations.
- The `delete_points` signature accepts `unique_id` as `wstring_view`, while `mountmgr_point::unique_id` stores raw bytes as `std::string`; unique IDs may not always be UTF-16 text.
