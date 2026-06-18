# File Research: sources/os/plan9/9front/sys/src/cmd/forp/logic.c

## Purpose
Builds compact SAT encodings for Boolean conjunction, disjunction, and arbitrary truth tables.

## Key Elements
Implements simplifying `satand1`, `sator1`, varargs wrappers, prime-implicant generation, implicant mask expansion, greedy cover selection, clause emission, and `satlogic1`/`satlogicv` for truth-table operators up to the supported arity.

## Dependencies
Uses global `satvar`, libsat `satadd1`/`sataddv`, and Plan 9 varargs adjustment via `satvafix`.

## Behavior/Risks
Constants are encoded as integer literals `1` and `2`, with negation used for complements. The truth-table minimizer uses dynamic global work arrays and a greedy cover, prioritizing compactness but not guaranteed minimum CNF.
