# File Research: sources/os/plan9/plan9/sys/src/cmd/touch.c

Plan 9 `touch` implementation.

Key responsibilities:
- Parses `-c` no-create and `-t time`.
- Uses current time by default, or an integer timestamp from `-t`.
- Updates file mtime through `dirwstat`.
- Creates missing files unless `-c` is set.
- Applies the selected mtime to newly created files via `dirfwstat`.

Notable behavior:
- Reports per-file errors and exits with `"touch"` if any file failed.
- `touch()` lacks an explicit return type in the old C style, effectively returning int.
