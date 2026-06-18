# File Research: sources/os/plan9/plan9/sys/src/cmd/tarsplit/tar.h

Shared tar-format header for `tarsplit`, `tarcat`, and `tarsub.c`.

Defines:
- `Tblock = 512`, `Namesz = 100`.
- Tar link flag values including plain file, hard link, symbolic link, directory, FIFO, and contiguous file.
- `Header` for pre-ustar tar headers through `linkname`.
- `Hblock`, a 512-byte union overlaying `Header`.

Utilities/macros:
- `islink`, `isreallink`, `issymlink`.
- `HOWMANY`, `ROUNDUP`, `TAPEBLKS` for tar block sizing.

Exports from `tarsub.c`:
- Global member names `thisnm`, `lastnm`.
- Archive helpers: `checksum`, `getdir`, `passtar`, `readtar`, `writetar`, `putempty`, `closeout`, `newarch`, `otoi`.

This header intentionally models only the classic tar header subset needed for stream splitting and concatenation.
