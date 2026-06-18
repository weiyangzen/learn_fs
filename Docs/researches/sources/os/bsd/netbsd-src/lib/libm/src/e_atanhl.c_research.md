# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_atanhl.c

Implements long-double `atanhl` when available, otherwise delegates to double `atanh`.

Key behavior:
- Checks long-double exponent/sign for domain and NaN-like cases.
- Uses format-specific tiny thresholds for 64-bit and 113-bit mantissas.
- Applies the same `log1pl` formulas as double `atanh`.
- Restores sign using the high sign bit.
