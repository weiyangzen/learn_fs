# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/main.c

Command-line driver for `htmlroff`.

- Supports `htmlroff [-iuv] [-m mac] [-r an] [file...]`.
- Initializes output `Biobuf`, `%L` line formatter, and quote formatting.
- `-m` queues a troff macro file from `/sys/lib/tmac/tmac.<name>`.
- `-r` initializes a number register from a compact `namevalue` argument.
- `-u` enables UTF-8 mode; `-v` enables verbose mode; `-i` forces stdin in addition to file inputs.
- Queues named files or stdin, then calls `run()` and terminates output.

Dependencies are `a.h` and the broader `htmlroff` request/parser implementation.
