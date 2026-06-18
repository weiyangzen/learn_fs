# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/unvac.c

Purpose: restore, list, or compare files from a Vac archive.

Command behavior:
- Options include table/list mode, verbose output, stdout extraction, diff/update mode, setting mtimes, Venti host selection, and statistics.
- Opens a Venti connection, opens the Vac archive read-only, gets the root, and recursively calls `unvac`.

Core functions:
- `wantfile` filters requested paths while allowing traversal through ancestors and descendants of requested names.
- `unvac` handles directory recursion, directory creation, file extraction, table output, and special-mode warnings.
- Diff mode opens an existing local file, compares block SHA1 via `sha1matches`, and writes only changed blocks.
- `writen` ensures full writes.
- `mtimefmt` formats mtimes for table output.

Integration points:
- Uses `vacfsopen`, `vacfsgetroot`, `vdeopen`/`vderead`, `vacfilewalk`, `vacfileread`, `vacfiledsize`, and `sha1matches`.
- Uses Plan 9 `Dir`, `dirmodefmt`, `dirwstat`, `create`, and `dirstat`.

Risks:
- Unsupported archived types such as device, symlink, named pipe, and exclusive file are warned and skipped.
- Diff mode removes a partially written output file on write errors.
- Path filtering is string-prefix based and depends on normalized archive names.
