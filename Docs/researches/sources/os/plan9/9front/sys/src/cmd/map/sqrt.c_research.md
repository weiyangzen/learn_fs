# File Research: sources/os/plan9/9front/sys/src/cmd/map/sqrt.c

Provides a local `sqrt(double)` implementation using `frexp()` scaling and Newton iteration.

Key behavior:
- Returns `0` for zero and negative inputs.
- Normalizes the input exponent, builds an initial estimate, rescales in chunks to avoid large shifts, and applies five Newton iterations.
- Contains an explicit note that the exponent parity trick does not work on ones-complement machines.

Important dependencies: Plan 9 libc `frexp`.

Notable risks:
- Negative inputs silently return `0` rather than setting domain errors.
- Integer shifts and old floating-point assumptions are portability-sensitive.
