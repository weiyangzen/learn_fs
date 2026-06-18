# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/getopt.c

Portable getopt implementation used by legacy PostScript tools.

Key responsibilities:
- Implements option parsing with global `opterr`, `optind`, `optopt`, and `optarg`.
- Supports grouped short options, option arguments, and `--`.

Important behavior:
- Returns `EOF` when options are exhausted.
- Prints diagnostics when `opterr` is set.

Notable risks:
- K&R-style signature omits the explicit `argc` parameter name in the function header, relying on old C conventions.
