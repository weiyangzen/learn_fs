# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/complex.c

Read fully: 85 lines, 1592 bytes. SHA-256 prefix: `6c05702d6df7af8e`.

Provides complex arithmetic helpers for map projections: robust-ish division `cdiv()`, multiplication `cmul()`, square `csq()`, square root `csqrt()`, and power `cpow()`.

`cdiv()` chooses the larger denominator component to reduce overflow/underflow risk. `csqrt()` uses magnitude-based formulas and preserves imaginary sign. `cpow()` uses polar exponentiation.

Integration: used by projections with conformal/elliptic transformations.

Risk notes: comments explicitly say addition/subtraction overflow is not guarded. `cpow()` is defined on one line in K&R-compatible style but with modern parameter declaration syntax.
