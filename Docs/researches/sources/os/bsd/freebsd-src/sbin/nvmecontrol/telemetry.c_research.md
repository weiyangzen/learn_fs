# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/telemetry.c

Purpose: Implements `nvmecontrol telemetry-log` for extracting host-initiated telemetry log data.

Key behavior:
- Registers top-level `telemetry-log`.
- Requires output file and data area 1-3, defaulting to data area 3.
- Opens controller or namespace, but rejects namespace operation after resolving controller because telemetry is controller/global.
- Verifies telemetry support through controller `lpa`.
- Reads the telemetry host-initiated log header, determines selected data-area end block, and writes all blocks up to that data area to the output file.
- Reads in 4096-byte chunks and optionally prints verbose progress.

Dependencies:
- `read_controller_data()`, `read_logpage()`, `open_dev()`, and `get_nsid()`.
- NVMe telemetry log page structures and `letoh()` conversion.

Research notes:
- Output file is opened with create/write but not truncate, so existing longer files could retain stale trailing content if overwritten with a smaller dump.
