# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/cpiofs.c

`cpiofs.c` is a read-only `tapefs` backend for several cpio archive variants.

Supported headers:
- Binary PWB 1.1 magic `0xc7 0x71`.
- ASCII `070707` sysiii-style octal headers.
- ASCII `070701` newc hex headers.

Parsing:
- Low-level readers `egetc`, `rd16le`, `rd3211`, `rdasc`, and `rdascx`.
- Header readers populate `Fileinf` with mode, uid/gid, mtime, size, and a static name buffer.
- `rdmagic` detects the header type and rejects mixed header formats in one archive.
- `populate` scans until `TRAILER!!!`, strips leading slashes, normalizes mode to directory/file/symlink/other, records file data offset, inserts into the `Ram` tree, and skips padded file contents.

Runtime:
- `doread` seeks to `r->addr + off` and reads into a static `dblock` buffer.
- Directories are fully populated during `populate`; `popdir` is a no-op.
- Writes are denied.

Risks:
- Header name buffers are limited to 256 bytes, matching historical implementation notes.
- Alignment handling differs by header flavor and is fatal on malformed archives.
