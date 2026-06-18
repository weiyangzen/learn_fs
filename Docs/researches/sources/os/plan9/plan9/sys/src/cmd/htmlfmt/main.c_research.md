# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlfmt/main.c

Command-line driver for `htmlfmt`.

- Supports `htmlfmt [-c charset] [-u URL] [-a] [-l length] [file ...]`.
- `-a` enables anchor/image/form annotations.
- `-u` sets the base URL and also enables annotation mode.
- `-c` injects a synthetic meta charset string and uses `charset()` to set default charset.
- `-l`/`-w` sets output wrap width.
- Processes stdin when no files are given, otherwise files in order until an error.

Dependencies are `dat.h`, Plan 9 `html.h`, and `loadhtml()` from `html.c`.
