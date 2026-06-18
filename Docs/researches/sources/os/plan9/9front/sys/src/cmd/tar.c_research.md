# File Research: sources/os/plan9/9front/sys/src/cmd/tar.c

`tar.c` implements Plan 9 `tar`: create/append/list/extract archives with ustar, selected GNU/PAX extensions, compression filters, and Plan 9 metadata handling.

Major features:
- Modes: `c`, `r`, `t`, `x`; archive file via `-f`; compression via `-z` or suffix detection.
- Optional resync on bad checksums, ignore read errors, keep existing files, relative path protection, set extracted times/metadata, POSIX toggle, uid/gid override.
- Compression uses child filters (`gzip`, `compress`, `bzip2` families) through `push`/`pushclose`.

Archive reading:
- Block buffering with configurable `nblock` based on `IOUNIT`.
- `readhdrblk` validates header checksum and supports resync.
- `readhdr` handles PAX per-file headers, PAX global headers, GNU long-name headers, and standard headers.
- `parsepax` recognizes `path`, `linkpath`, `uname`, `gname`, `atime`, `mtime`, and `size`.
- Supports GNU/base-256 large size encoding.

Archive writing:
- `addtoar` stats files, emits PAX path headers for long names, writes headers through `mkhdr`, recursively descends directories, and writes file data in tar blocks.
- `replace` creates or appends archives and writes two zero end markers.

Extraction/listing:
- `match` selects requested prefixes.
- `extract1` protects absolute paths and Plan 9 `#` names when relative mode is enabled, creates files/dirs, skips unsupported links/fifos, copies data, and optionally writes metadata.
- Table mode prints either plain names or verbose `%M` mode/size/time/name.

Risks:
- Link and FIFO extraction is not implemented.
- Directory metadata is applied immediately, not after all children.
- `parsehdr` appears to fill `hdr->gid` from `bp->uname` instead of `bp->gname`, likely a bug.
