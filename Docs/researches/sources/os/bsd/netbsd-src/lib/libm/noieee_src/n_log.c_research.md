# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_log.c

Implements no-IEEE natural logarithm entry points for `log`, `logf`, and long-double aliases using Peter Tang's table-driven logarithm algorithm.

Key behavior:
- Handles zero, negative, infinity, and NaN differently for IEEE versus VAX/Tahoe paths.
- Reduces `x` into `2^m * F * (1 + f/F)`, with `F` chosen from a 129-entry table.
- Uses split `logF_head`/`logF_tail` tables and polynomial correction terms `A1` through `A4`.
- Provides `__log__D(double)` returning a `struct Double` split result for extended-precision consumers such as `pow`.
- `logf` delegates to double `log`.

Notable risks:
- The IEEE truncation macro type-puns through `int *` and is endian-sensitive.
- The file exposes both public aliases and internal helper behavior, so changes can affect `pow`/gamma-style split-precision code.
