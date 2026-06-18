# File Research: sources/os/plan9/9front/sys/src/cmd/disk/mkfs.c

Proto-file driven filesystem/archive population tool.

Key behavior:
- Reads one or more proto files through `rdproto`.
- In filesystem mode, copies files from a source root to a destination root, creates directories, updates modes/times/groups, and optionally uid/gid.
- In archive mode (`-a`), emits `mkext`-compatible headers plus file contents to stdout.
- Supports ream/force behavior, mode-only updates, verbose logging, source/destination prefixes, listing modes `-x`/`-o`, and configurable copy buffer.
- File copying uses a temp sibling `__mkfstmp`, sparse zero skipping, and final `dirfwstat` rename semantics.

Notable dependencies:
- `libproto` via `rdproto`, Plan 9 `Dir` metadata, `Biobuf`.

Research notes:
- `uptodate` skips copying existing destination files whose mtime is newer unless reaming/archive mode.
- Archive mode and `mkext.c` are paired formats.
