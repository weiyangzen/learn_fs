# File Research: sources/virtualization/guestfs-tools/gnulib/lib/xstrtol.c

Macro-parameterized implementation of robust string-to-integer parsing.

Behavior:
- Defaults to `long int`/`strtol`/`xstrtol` unless included with macros redefining target type and conversion function.
- Rejects negative input for unsigned target types.
- Returns `strtol_error` flags instead of only relying on `errno`.
- Supports valid suffix checking.
- Supports suffix scaling:
  - `b` = 512
  - `B` = 1024 legacy
  - `c` = no scale
  - `k/K`, `M/m`, `G/g`, `T/t`, `P`, `E`, `Z`, `Y`
  - optional `B` or `iB` second suffix when valid suffix list contains `0`.
- Detects scaling overflow and clamps to min/max.

Research relevance: common safe parser for numeric command-line arguments and block-size-like values.
