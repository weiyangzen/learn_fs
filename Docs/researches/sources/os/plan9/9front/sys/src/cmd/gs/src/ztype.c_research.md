# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ztype.c

## Purpose
Implements PostScript type inspection, access attributes, executable/literal conversion, and scalar/string conversion operators.

## Key Elements
Defines `.type`, `.typenames`, `cvlit`, `cvx`, `xcheck`, `executeonly`, `noaccess`, `readonly`, `rcheck`, `wcheck`, `cvi`, `cvn`, `cvr`, `cvrs`, and `cvs`.

## Behavior/Risks
`cvx` rejects internal operators outside the exec stack. Access checks handle dictionaries through dictionary access refs and include special restrictions for permanent/read-only dictionaries. Numeric conversions parse strings through the scanner and enforce integer range with real bounds. `cvrs` handles radix 2 through 36 and reuses `cvs` logic for radix 10. `cvs` has a compatibility hack that truncates internal operator names beginning with `%`, `.`, or `@` on rangecheck.

## Dependencies
Uses scanner, name, dictionary stack, ref access flags, interpreter utility conversion routines, and object-to-string formatting from `iutil.h`.
