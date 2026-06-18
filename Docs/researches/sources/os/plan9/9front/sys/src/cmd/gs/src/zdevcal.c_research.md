# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdevcal.c

Defines the special `%Calendar%` IODevice.

Key behavior:
- Registers `gs_iodev_calendar` as a special read-only device with only `get_params` implemented.
- `calendar_get_params` writes current local time fields: Year, Month, Day, Weekday, Hour, Minute, and Second.
- Adds a `Running` boolean that is true when `time()` and `localtime()` succeed, false when time lookup fails.
- Converts `tm_year` to full year and `tm_mon` to one-origin month before returning.

Dependencies:
- Uses Ghostscript IODevice and parameter-list interfaces plus C runtime time functions.

Research notes:
- This is not file I/O; it exposes process-local clock data through the PostScript IODevice parameter mechanism.
