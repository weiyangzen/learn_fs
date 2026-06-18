# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/utils.c

`utils.c` contains common Venti server helpers: bounded arena-name compare/copy/validation, decimal `u32int`/`u64int` parsing with overflow checks, Venti type validation, error/log formatting, current time, `u64log2`, process creation wrapper, formatters, millisecond time, and bit counting.

`ventifmtinstall()` installs formatting for Venti calls, hex, index entries, time, and scores. `seterr()` updates Plan 9 `%r` error text while optionally logging severity-tagged messages.

These utilities are small but widely shared across admin tools and server paths.
