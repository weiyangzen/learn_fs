# sources/user-network-fs/nfs-utils/support/nfs/nfs_mntent.c

Purpose: private mount-entry parser/writer similar to libc `mntent`, with explicit escaping for whitespace and backslashes.

Important APIs: `nfs_setmntent()`, `nfs_endmntent()`, `nfs_addmntent()`, and `nfs_getmntent()`. Internal helpers `mangle()` and `unmangle()` encode/decode `\040`-style octal escapes.

Control flow: opening temporarily sets umask 077. Writing seeks to EOF, records current length, writes escaped fields plus numeric freq/passno, flushes, and truncates back to the previous length on flush failure. Reading skips blank/comment lines, handles missing final newline warnings, unmangles four fields, parses optional numeric freq/passno, and skips malformed lines until an error threshold.

State and persistence: `mntFILE` owns file pointer, path, line number, and soft/hard error counters. `nfs_getmntent()` returns a static `struct mntent` backed by heap strings that are replaced on each call.

Dependencies and integration: used by mount-related nfs-utils code. Depends on `xcommon` allocation/error helpers and NLS `_()` messages.

Risks: returned entries are static and not thread-safe; repeated calls leak or overwrite expectations unless caller understands ownership. Line length is capped at 4096. Parser tolerates trailing data, so corrupted lines may not always fail.

Test signals: escaped spaces/tabs/newlines/backslashes, bad lines and `ERR_MAX`, missing final newline, flush failure rollback, append semantics, and `/proc/mounts`-like files.
