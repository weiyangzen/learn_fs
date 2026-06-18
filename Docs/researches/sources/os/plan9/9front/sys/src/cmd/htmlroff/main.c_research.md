# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/main.c

Provides the `htmlroff` command entry point.

Key points:
- Converts troff `-ms`-style input to HTML.
- Options:
  - `-i` also reads stdin after named inputs.
  - `-m mac` queues `/sys/lib/tmac/tmac.<mac>`.
  - `-r an` sets a one-letter number register to the supplied value.
  - `-u` is accepted as legacy/default.
  - `-v` enables verbose warnings/debug output.
- Queues named input files or stdin, initializes output `Biobuf`, installs `%L` line formatter, then calls `run`.
- Emits a final newline, flushes output, and exits.

Dependencies and interactions:
- Uses input queueing from `input.c`, register setting from `t8.c`, and the main interpreter in `roff.c`.

Research relevance:
- Defines command-line integration for the roff-to-HTML interpreter.
