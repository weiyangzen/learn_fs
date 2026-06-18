# sources/user-network-fs/samba/source4/ntvfs/simple/svfs_util.c

Purpose: `svfs_util.c` provides utility functions for the simple NTVFS backend: path conversion, directory wildcard listing, fd-based utime support, and Unix-to-DOS attribute mapping.

Important APIs, types, and functions: Functions are `svfs_unix_path`, `svfs_list_unix`, `svfs_list`, `svfs_file_utime`, and `svfs_unix_to_dos_attrib`.

Control flow: `svfs_unix_path` lowercases the incoming SMB path, prepends the share connect path, and converts backslashes to slashes. `svfs_list_unix` splits the requested pattern into directory and mask, opens the directory, lowercases names, filters with `ms_fnmatch_protocol`, skips stream-like names unless requested, stats matches, and grows a talloc array. `svfs_file_utime` updates times through a `/proc/self/<fd>` path.

State and persistence behavior: Directory listings are snapshots allocated under the caller's talloc context. `svfs_file_utime` persists access/write timestamps. Other functions only map or inspect filesystem state.

Dependencies and integration points: It depends on Samba wildcard matching, `system/dir.h`, `system/time.h`, POSIX `opendir/readdir/stat/utime`, and the simple backend structs. `vfs_simple.c` uses it for query info and searches.

Risks: Lowercasing every path is not a correct general SMB case policy. `/proc/self/<fd>` is nonportable and likely wrong on platforms without procfs or with different fd path syntax. Directory listing allocation growth uses integer math and should be watched for large directories.

Test signals: Tests should validate wildcard matching, stream name filtering, mixed slash input, case behavior, large directories, missing directories, and timestamp setting through open fds.
