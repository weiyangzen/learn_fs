# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/tarfs.c

`tarfs.c` is a read-only `tapefs` backend for tar archives.

Format support:
- Handles 512-byte tar headers, old-style names, POSIX ustar prefix/name, GNU long-name records, directory flags, symlink/hardlink flags, and big binary size marker `0x80`.
- `tarname` reconstructs full ustar paths.
- `checksum` validates each header by treating checksum bytes as spaces.

Population:
- `populate` scans archive blocks, computes metadata, normalizes unsafe paths by stripping leading `/`, `cleanname`, and removing leading `../`.
- Directories are detected by tar linkflag, mode, or trailing `/`.
- Link records are skipped as zero-sized entries.
- GNU long-name records set `nextname` for the following real record.
- Accepted entries are inserted via `poppath`.

Reads:
- `doread` seeks to `512 * r->addr + off`, reads with `readn`, and zero-fills short reads.
- Directories are eager; `popdir` is a no-op.
- Writes are denied.

Risks:
- Does not materialize symlink targets; links are effectively skipped/zero-sized.
- Only a subset of modern tar extensions is supported compared with `cmd/tar.c`.
