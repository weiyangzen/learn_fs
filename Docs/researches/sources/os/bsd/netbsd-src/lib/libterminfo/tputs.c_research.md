# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/tputs.c

Terminal output and padding implementation.

Key responsibilities:
- Defines global termcap variables:
  - `ospeed`
  - `PC`
- Parses leading and embedded delay expressions, including mandatory `/` delays and multiplied `*` delays.
- Emits padding characters based on baud-rate-derived timing table.
- Implements explicit-terminal output:
  - `ti_puts`
  - `ti_putp`
- Implements classic output:
  - `tputs`
  - `putp`

Important behavior:
- `ti_puts` only delays for bell/flash or when padding is needed because xon/xoff is not available and padding baud rate is set.
- `tputs` always allows delay processing using global `ospeed` and `PC`.

Role in subsystem:
- Final output layer for expanded terminal control strings.
