# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_log2.c

Implements no-IEEE `log2`, `log2f`, and long-double aliases.

Key behavior:
- Computes base-2 logarithm by dividing natural log by a static `ln2`.
- `log2` calls `log(x)`.
- `log2f` calls `logf(x)`.
- Special cases are inherited from the underlying natural logarithm routines.

The header comment incorrectly says “base 10 logarithm,” but the code implements base 2.
