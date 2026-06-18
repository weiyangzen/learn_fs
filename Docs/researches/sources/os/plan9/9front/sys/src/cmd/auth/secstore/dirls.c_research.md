# File Research: sources/os/plan9/9front/sys/src/cmd/auth/secstore/dirls.c

Directory listing formatter for secstore.

Key responsibilities:
- Reads all directory entries for a path and sorts by name.
- Computes SHA1 digest for each listed file.
- Formats lines with aligned name, size, ctime-derived timestamp, and base64 SHA1 digest.
- Returns the accumulated listing as a newly allocated string.

Dependencies:
- Uses Plan 9 `dirreadall`, `dirstat`, SHA1, base64 encoding, and secstore allocation helpers.

Notable risks:
- `sha1file` returns nil for unreadable files, but listing code assumes a digest pointer when encoding.
