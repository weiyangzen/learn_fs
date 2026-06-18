# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/Makefile

Builds the OpenBSD `pfctl` packet-filter control utility.

Key contents:
- Sets `PROG=pfctl`.
- Builds from:
  - `pfctl.c`
  - `parse.y`
  - `pfctl_parser.c`
  - `pf_print_state.c`
  - `pfctl_osfp.c`
  - `pfctl_radix.c`
  - `pfctl_table.c`
  - `pfctl_optimize.c`
  - `pf_ruleset.c`
  - `pfctl_queue.c`
- Enables `-Wall`, `-Wmissing-prototypes`, `-Wstrict-prototypes`, and includes the current directory.
- Leaves `YFLAGS` empty for yacc processing of `parse.y`.
- Installs `pfctl.8`.
- Adds `.PATH` to `../../sys/net` for ruleset and anchor handling sources.
- Links against `libm`.
- Includes OpenBSD `bsd.prog.mk`.

Research notes:
- `pf_ruleset.c` is pulled from the kernel network source path rather than the local `sbin/pfctl` directory.
- The parser, optimizer, table handling, queue handling, state printer, and main control program are built into one utility.
