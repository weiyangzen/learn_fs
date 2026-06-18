# File Research: sources/local-fs/dosfstools/src/testdevinfo.c

Small diagnostic utility that opens a supplied file/device, calls dosfstools device probing, and prints the discovered metadata in human-readable form.

Key elements:
- Expects exactly one argument: `FILENAME`.
- Opens the target read-only with `O_NONBLOCK`.
- Sets `device_info_verbose = 100` to force verbose probing.
- Calls `get_device_info(fd, &info)`.
- Prints:
  - device type
  - partition status/number
  - whether the device has children
  - geometry heads
  - geometry sectors
  - geometry start
  - total disk sectors
  - sector size
  - byte size

Dependencies:
- Includes `device_info.h`.
- Uses device type constants:
  - `TYPE_UNKNOWN`
  - `TYPE_BAD`
  - `TYPE_FILE`
  - `TYPE_VIRTUAL`
  - `TYPE_REMOVABLE`
  - `TYPE_FIXED`

Research notes:
- This is a debug/test helper for the device discovery layer, not part of the formatter path.
- Unknown values are represented by negative fields in `struct device_info` and printed as `unknown`.
- The program does not fail if `get_device_info` reports unusable or unknown metadata; it prints whatever was collected.
