# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zstack.c

## Purpose
Implements core PostScript operand-stack operators for Ghostscript.

## Key Elements
Defines `pop`, `exch`, `dup`, `index`, `roll`, `clear`, `count`, `mark`, `cleartomark`, and `counttomark`. The public operator table is `zstack_op_defs`.

## Behavior/Risks
`index` and `roll` handle stack entries that may span older stack blocks through `ref_stack_index` and `ref_stack_count`. `roll` has optimized common cases for `1` and `-1`, and slower multi-block rotation for deep stack ranges. Range and stack checks are explicit and return PostScript errors such as `rangecheck`, `stackoverflow`, and `unmatchedmark`.

## Dependencies
Uses interpreter stack primitives from `istack.h`, allocation context from `ialloc.h`, operand macros from `oper.h`, and ref assignment/store helpers from `store.h`.
