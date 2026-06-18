# File Research: sources/virtualization/libguestfs/daemon/echo-daemon.c

Implements daemon-side echo.

Key points:
- `do_echo_daemon` joins argv strings with spaces using `guestfs_int_join_strings`.
- Returns the joined string.
- Only failure path is allocation failure.
