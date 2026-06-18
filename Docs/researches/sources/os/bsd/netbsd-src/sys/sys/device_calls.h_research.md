# File Research: sources/os/bsd/netbsd-src/sys/sys/device_calls.h

Generated typed wrappers for generic device autoconfiguration calls.

Key content:
- Generated from `device_calls`; file warns not to edit manually.
- Includes `<sys/device.h>`.
- `device-enumerate-children` args and binding macro.
- `device-register` args and binding macro.
- `device-is-system-todr` optional RTC/TODR filter.
- `device-get-property` args and binding macro, with extensive contract documentation for property type, size, encoding, and errors.

Important behavior:
- Uses `struct device_call_generic` compatibility so typed wrappers can be passed to `device_call`/`devhandle_call`.
- Documents strict property retrieval rules for data, strings, numbers, booleans, and unknown-type queries.
- Error contract includes `ENOENT`, `EFBIG`, `EFTYPE`, `EINVAL`, and `EIO`.
