# File Research: sources/os/plan9/9front/sys/src/cmd/cp.c

Plan 9 `cp` implementation for file-to-file and file-to-directory copying. It rejects directory sources and detects source/destination identity via qid, dev, and type.

Important behavior:
- Options: `-x` preserves mode and mtime, `-g` preserves gid, `-u` preserves uid and gid.
- Uses `iounit()` or `IOUNIT` to size the copy buffer.
- Copies using plain `read()`/`write()` loop in `copy1()`.
- Creates destination with source permission bits masked to `0777`.
- Metadata preservation uses `dirfwstat()` after successful content copy.
