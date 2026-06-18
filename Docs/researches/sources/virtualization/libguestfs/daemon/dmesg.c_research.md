# File Research: sources/virtualization/libguestfs/daemon/dmesg.c

Simple wrapper for appliance kernel log output.

Key points:
- `do_dmesg` runs external `dmesg`.
- Returns stdout as caller-owned string.
- Captured stderr is used for daemon error reply on failure.
