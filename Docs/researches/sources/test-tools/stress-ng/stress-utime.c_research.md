## sources/test-tools/stress-ng/stress-utime.c

Purpose: Implements `utime`, stressing timestamp update APIs over normal, invalid, boundary, and optional fsync paths.

Important APIs/types/functions: `stress_utime_info`, `stress_utime_str`, and `stress_utime`; options include `utime-fsync`. Uses `utimes`, `futimens`, `utimensat`, `utime`, `pathconf(_PC_TIMESTAMP_RESOLUTION)`, `O_PATH` directory fds, bad fd helpers, and temp fs helpers.

Control flow: creates one temp file, then loops through many timestamp update variants: current time, NULL timestamps, invalid names, huge names, FAT-era/2038/boundary values, `UTIME_NOW`, `UTIME_OMIT`, invalid flags, directory-fd empty path, and `AT_SYMLINK_NOFOLLOW`. Every thousand operations it records timing samples.

State and persistence: temp directory/file and optional directory fd are cleaned on exit; no persistent timestamp state remains.

Dependencies/integration: compile-gated timestamp APIs, stress-ng verify flag, filesystem type diagnostics, and metrics.

Risks: filesystem-specific timestamp ranges/resolution can make some probes fail or be ignored; optional verification only checks times are not earlier than requested.

Test signals: `VERIFY_OPTIONAL`; metrics report utime calls/sec and verification reports atime/mtime regressions.
