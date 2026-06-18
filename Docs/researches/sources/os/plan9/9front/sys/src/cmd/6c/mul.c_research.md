# File Research: sources/os/plan9/9front/sys/src/cmd/6c/mul.c

- Role: Strength reduction for multiplication by constants in the 6c amd64 backend.
- Defines small cached `Mparam` plans and algorithm tables used to express constants as shifts, adds/subtracts, and LEA-style scaled addressing.
- `lowbit()` finds the index of the lowest set bit in a 32-bit unsigned value.
- `mulparam()` searches candidate decomposition patterns and records an algorithm when a multiply can be done within a small cost threshold.
- `genmuladd()` builds an indexed-address expression and emits an address calculation, using amd64 addressing modes for multiply-add forms.
- `m0()`, `m1()`, and `m2()` map selected multiplier fragments to LEA scale factors.
- `shiftit()` emits either no-op, add-self, or shift-left for constant powers.
- `mulgen()` tries `mulgen1()` for optimized constant multiplication and falls back to `gopcode(OMUL, ...)` when no good decomposition exists.
