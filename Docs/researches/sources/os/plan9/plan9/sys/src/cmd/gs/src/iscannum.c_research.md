# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscannum.c

Purpose: implements the performance-sensitive number scanner used by `iscan.c`.

Supported syntax and behavior:
- Decimal integers, reals with fractional and exponent parts, signed numbers, radix numbers using `radix#digits`, and overflow promotion from int to long to double accumulation.
- Returns 0 when the whole input range is consumed as a number, or 1 with `*psp` pointing after the numeric prefix when trailing non-number data exists.
- Produces integer refs when possible and real refs when decimal/exponent/overflow requires it.
- Checks integer/unsigned/radix overflow and real range against `MAX_FLOAT`.

Optimization details:
- Fast path accumulates up to four leading decimal digits without a loop.
- Powers of ten up to 1e6 are table-driven for real scaling.
- Power-of-two radix parsing uses shifts instead of multiplication.

Compatibility detail: `PDFScanInvNum` allows Adobe-compatible handling of bogus `-` characters after a decimal point by swallowing the rest of the fractional digits rather than treating them as a scanner error.

Research notes: The file comments acknowledge the "spaghetti" control flow as a deliberate scanner hot-path optimization.
