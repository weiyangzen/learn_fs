# File Research: sources/os/plan9/9front/sys/src/cmd/vac/unvac.c

Purpose: Extracts, lists, or incrementally updates files from a Vac archive.

Key behavior:
- Opens a Vac archive read-only from a Venti server and recursively walks from the root.
- Supports stdout extraction (`-c`), diff/update mode (`-d`), table/list mode (`-t`), mtime restoration (`-T`), stats (`-s`), host selection, and verbosity.
- Filters extraction by requested path prefixes and tracks missing requested files.
- Skips unsupported stored types such as devices, links, named pipes, and exclusive lock files.
- Creates directories and files with stored permissions unless listing or writing to stdout.
- In diff mode, opens an existing file read/write, compares existing blocks with stored block scores via `sha1matches`, and writes only changed data.
- Optionally restores modification time after extraction.

Dependencies:
- Uses `vacfsopen`, `vacfsgetroot`, `vdeopen`/`vderead`, `vacfilewalk`, `vacfileread`, `vacfiledsize`, `sha1matches`, and Plan 9 `Dir`/`dirmodefmt`.

Notable details:
- `wantfile` includes both ancestors and descendants of requested paths so traversal reaches selected leaves.
- Diff extraction truncates via `dirfwstat` when a partial final read shortens an existing file.
