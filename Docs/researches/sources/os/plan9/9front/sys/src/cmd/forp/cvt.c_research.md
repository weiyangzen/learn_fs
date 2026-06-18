# File Research: sources/os/plan9/9front/sys/src/cmd/forp/cvt.c

## Purpose
Converts parsed `forp` bit-vector expressions into SAT variables and clauses.

## Key Elements
Maps symbols and numeric constants to bit vectors, assigns lvalues, implements equality, bitwise logic, logical operators, complement, negation, addition/subtraction, comparisons, indexing, shifts, ternary, multiplication, absolute value, division/modulo constraints, `assume`, `obviously`, and SAT initialization with constants false/true.

## Dependencies
Uses Plan 9 `mpint`, libsat primitives, AST definitions from `dat.h`, parser nodes, and helper SAT logic combinators from `logic.c`.

## Behavior/Risks
Arithmetic is encoded at bit level with sign extension for signed values and an extra sign/zero bit for unsigned symbols. Division introduces quotient/remainder variables and constraints rather than computing directly. Unsupported operators call `error` or abort.
