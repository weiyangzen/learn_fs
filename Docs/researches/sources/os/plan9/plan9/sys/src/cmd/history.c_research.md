# File Research: sources/os/plan9/plan9/sys/src/cmd/history.c

Plan 9 dump filesystem history lookup utility.

- Supports `history [-bDfuv] [-d dumpfilesystem] [-s yyyymmdd] files`.
- Resolves each target file to an absolute path and maps `/n/<name>/...` paths to a corresponding `<name>dump` mount unless `-d` is supplied.
- Ensures the dump filesystem is mounted by running `9fs <dump>` when needed.
- Prints current file state, then walks backward through dump snapshots to find earlier versions.
- Supports both traditional dump naming and `snap`-style directories.
- With `-D`, runs `/bin/diff` between adjacent found versions, forwarding selected diff flags.

Important functions: `ysearch`, `lastbefore`, `starttime`, `prtime`, and `darg`.

Notable concerns:
- Time search uses heuristic 12-hour/day stepping and a 30-try backward limit.
- Buffers for paths are fixed-size.
- With `-f`, missing historical files are represented by synthetic `Dir` data to continue reporting removals.
