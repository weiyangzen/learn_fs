# File Research: sources/local-fs/udftools/cdrwtool/options.h

Small public header for `cdrwtool` option handling.

Declares:
- `usage(void)`
- `parse_args(int, char *[], struct cdrw_disc *, const char **)`

Includes `<getopt.h>` for option handling.

Defines `OPT_HELP` as a long-option token in the `0x1000` range. Comments reserve token ranges for short options, long switches, and long settings.

No runtime logic.
