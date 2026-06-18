# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/mul.c

## Purpose
Optimizes multiplication by constants for the 386 backend using shifts, adds, subtracts, and scaled addressing where cheaper than `IMUL`.

## Key Functions
- `lowbit()` finds the lowest set bit position.
- `genmuladd()` emits scaled-index address-generation multiplication/addition.
- `mulparam()` selects a multiplication algorithm for a constant.
- `m0()`, `m1()`, and `m2()` map special constants to scale factors.
- `shiftit()` emits efficient shift-left or add-for-times-two.
- `mulgen1()` emits selected optimized multiplication sequence.
- `mulgen()` falls back to `OMUL` when no optimized sequence is chosen.

## Important Behavior
- Caches recent constant multiplication parameters in `multab`.
- Recognizes constants expressible through combinations of shifts and scaled-index LEA forms.
- Handles negative multipliers by negating or subtracting as needed.
- Uses x86 scaled addressing to synthesize multiplication by small factors efficiently.

## Research Notes
This complements `div.c`: both perform arithmetic strength reduction before final instruction selection.
