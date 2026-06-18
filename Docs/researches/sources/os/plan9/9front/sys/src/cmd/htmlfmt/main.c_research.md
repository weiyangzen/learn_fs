# File Research: sources/os/plan9/9front/sys/src/cmd/htmlfmt/main.c

Provides option parsing, charset conversion setup, and file iteration for `htmlfmt`.

Key points:
- Options:
  - `-a` prints full URLs/images/form markers inline.
  - `-c charset` selects input charset for `/bin/uhtml`.
  - `-l`/`-w` sets wrap width.
  - `-u URL` sets base URL.
- `uhtml` runs `/bin/uhtml -c <charset>` through a pipe, falling back to `/bin/cat` in the child if `uhtml` exec fails.
- Processes stdin when no files are supplied, otherwise opens each file and passes it through `uhtml` into `loadhtml`.
- Reports processing errors with the file name and exits with the error string.

Dependencies and interactions:
- Uses `loadhtml` from `html.c`.
- Uses Plan 9 process, pipe, fd, and exec primitives.

Research relevance:
- This file defines how `htmlfmt` is invoked and how charset normalization is inserted before parsing.
