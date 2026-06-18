# File Research: sources/os/plan9/plan9/sys/src/cmd/primes.c

Purpose: Prints prime numbers in an optional numeric range.

Key behavior:
- Accepts `start [finish]`; if no args, reads first nonblank line from stdin as start.
- Prints small primes from a fixed table before switching to segmented sieve.
- Uses a 1000-byte bit table representing 8000 candidate offsets.
- Uses a wheel increment table after marking 3, 5, and 7.
- `mark` marks multiples of a factor within the current segment.
- Supports values up to `big` around 2^53.

Dependencies and integration:
- Uses Plan 9 libc/Bio and floating-point arithmetic for large integer-ish values.

Risks and notes:
- Floating-point representation limits exactness for very large values.
- Does not explicitly skip composite odd values below current segment except through marking.
- `limit < nn` check in two-argument path occurs before `nn` is set from start, but default `nn` is 0, so only negative/zero edge cases are affected.
