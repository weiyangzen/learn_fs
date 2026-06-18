# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_log10.c

Implements no-IEEE `log10`, `log10f`, and long-double aliases.

Key behavior:
- Uses `log(x)` as the kernel.
- On VAX/Tahoe, divides by a high-precision `ln10hi`.
- On IEEE-style targets, multiplies by `ivln10`.
- `log10f` delegates through `logf` on VAX/Tahoe and through double `log` otherwise.

Special cases are inherited from `log`.
