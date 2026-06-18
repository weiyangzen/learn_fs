# File Research: sources/virtualization/nvme-cli/plugins/wdc/wdc-utils.h

Header for WDC plugin utility helpers.

Key elements:
- Defines WDC utility status codes for success, invalid parameter, memory errors, file/directory errors, and archive-related failures.
- Defines constants for firmware revision length, serial length, seconds per minute, and max path length.
- Defines `UtilsTimeInfo`, a simple local-time structure with year/month/day/hour/min/sec, DST flag, milliseconds, and timezone offset.
- Declares WDC string, file, directory, time, formatting, and UUID-list support helpers.

Dependencies:
- Pulls in standard C headers, POSIX stat/time headers, and expects libnvme types for `struct libnvme_transport_handle` and `struct nvme_id_uuid_list`.

Notes:
- This header includes many implementation headers directly; users get a broad include surface.
