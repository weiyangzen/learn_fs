# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zvmem2.c

## Purpose
Implements Level 2 VM-space and garbage-collector control operators.

## Key Elements
Provides `.setglobal`, `.currentglobal`, `gcheck`, and Level 2 `.vmreclaim`. Exports `set_vm_threshold()` and `set_vm_reclaim()` for `setuserparams`.

## Behavior/Risks
`.setglobal` switches allocation between global and local VM. `gcheck` reports whether an object is not local. `set_vm_threshold` normalizes `-1` and clamps thresholds before setting global and local thresholds. `set_vm_reclaim` enables/disables GC independently for system/global/local spaces according to values `-2` through `0`. `.vmreclaim` forces interpreter exit via `e_VMreclaim` for immediate collection requests `1` or `2`.

## Dependencies
Uses VM-space macros from `ivmspace.h`, memory GC control via `ivmem2.h`, and operand/ref helpers.
