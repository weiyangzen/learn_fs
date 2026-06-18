# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ztrap.c

## Purpose
Provides minimal LanguageLevel 3 trapping parameter operators.

## Key Elements
Defines global `i_trap_params`, `.settrapparams`, and `settrapzone`.

## Behavior/Risks
The source marks the trap-parameter storage as bogus, and `settrapzone` is explicitly not implemented, returning `undefined`. `.settrapparams` reads a dictionary into a parameter list and delegates validation/application to `gs_settrapparams`.

## Dependencies
Uses dictionary parameter-list helpers from `iparam.h` and trap support from `gstrap.h`.
