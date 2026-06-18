# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_config.h

Configuration and platform compatibility header for ext4srv.

Key behavior:
- Includes Plan 9 `u.h` and `libc.h`.
- Defines a local `bool` enum.
- Defines open flag constants used by the ext4 library and an `O_WRMASK`.
- Detects several big-endian architectures and defines `CONFIG_BIG_ENDIAN`.
- Defines static limits for block devices, mountpoints, block cache size, and max single truncate size.
- Declares global Plan 9-style error strings used across the implementation.

Notable dependencies:
- Included by nearly all ext4srv headers and C files.

Research notes:
- Open flag values follow Unix-style bit assignments, not Plan 9's public flag values; `ext4srv.c` translates Plan 9 open modes before calling ext4.
