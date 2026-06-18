# File Research: sources/os/plan9/9front/sys/src/cmd/primes.c

Prime number generator. It accepts optional start and finish bounds, or reads a start from stdin, prints small primes from a table, then repeatedly sieves odd ranges using a wheel pattern and a 1000-byte bit table.

Key behavior:
- Bounds are stored as `double`, with a max near `2^53`.
- `mark` marks multiples of a prime in the current range.
- Uses small-prime table through 229 and wheel increments for candidate factors.

Integration points:
- Standalone command using Plan 9 `Biobuf` and `print`.

Risks:
- Floating-point arithmetic is used for integer-like bounds; valid range is capped to exact integer representation.
- `mark` uses a long index derived from double math; behavior depends on staying within supported limits.
