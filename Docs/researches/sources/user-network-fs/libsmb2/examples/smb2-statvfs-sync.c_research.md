# sources/user-network-fs/libsmb2/examples/smb2-statvfs-sync.c

## Purpose
`smb2-statvfs-sync.c` is a synchronous example that reports filesystem capacity for an SMB URL path. It demonstrates `smb2_statvfs()` after URL parsing and share connection.

## Important APIs, Types, and Functions
The file uses `usage()`, `smb2_init_context()`, `smb2_parse_url()`, `smb2_set_security_mode()`, `smb2_connect_share()`, `smb2_statvfs()`, `smb2_disconnect_share()`, `smb2_destroy_url()`, and `smb2_destroy_context()`. Output comes from `struct smb2_statvfs`, especially `f_bsize`, `f_blocks`, `f_bfree`, and `f_bavail`.

## Control Flow
After argument validation, the program builds an SMB2 context and URL, enables signing capability, connects to the target share, calls `smb2_statvfs(smb2, url->path, &vfs)`, prints block size and allocation counts, then disconnects and frees resources.

## State and Persistence Behavior
State is limited to the connection context, parsed URL, and stack statvfs structure. The remote share is queried but not modified. Error exits before the final cleanup leak the context and URL for process lifetime.

## Dependencies and Integration Points
The example depends on libsmb2 high-level APIs and standard integer formatting. It conditionally excludes `<poll.h>` on Amiga-like targets, showing that examples are expected to compile on some non-POSIX platforms.

## Risks and Edge Cases
Only a subset of `struct smb2_statvfs` is printed, so file count/name-length fields are not demonstrated. `f_bsize` is printed with `%d` despite being `uint32_t`. The signing setting is enabled, not required, and URL parse/init failures exit with status `0`.

## Test Signals
Exercise root paths and subpaths on shares with quotas, full volumes, permission restrictions, and servers with large allocation-unit counts. Verify `PRIu64` output and behavior on unsupported filesystem-info classes.
