# File Research: sources/os/plan9/9front/sys/src/cmd/forp/forp.c

## Purpose
Main driver and result printer for the `forp` SAT-based formula prover.

## Key Elements
Prints model values for bit symbols, can dump SAT clauses for debugging, formats all model rows in `-m` mode, adds collected `obviously` negations as a disjunction, proves by unsatisfiability or prints a counterexample model, initializes formatters and subsystems, parses stdin or one file, and runs the solver.

## Dependencies
Uses global SAT state from `cvt.c`, symbol list from `misc.c`, parser/converter initialization, libsat solving APIs, and Plan 9 format installation.

## Behavior/Risks
If no `obviously` assertion is present, it exits with a message instead of solving. In normal mode, `satsolve(sat) == 0` is interpreted as proof; otherwise symbol values are printed with unknown bits as `?`.
