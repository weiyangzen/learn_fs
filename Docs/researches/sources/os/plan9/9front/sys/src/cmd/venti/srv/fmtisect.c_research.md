# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/fmtisect.c

Formats a physical index-section partition/file.

Key behavior:
- CLI: `fmtisect [-Z] [-b blocksize] name file`, plus `-1` for old section version.
- Defaults: 8 KiB block size, 512 KiB section table size, `ISectVersion2`.
- Optionally zeroes the partition.
- Creates a new `ISect` and writes its header/table with `wbisect`.
- Prints bucket count, entries per bucket, and table size.

Interactions:
- Uses `newisect`, `zeropart`, and `wbisect`.

Notable details:
- Version 1 defaults to zeroing, version 2 defaults not to zero unless `-Z`.
