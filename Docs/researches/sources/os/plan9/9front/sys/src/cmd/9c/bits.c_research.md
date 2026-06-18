# File Research: sources/os/plan9/9front/sys/src/cmd/9c/bits.c

Bitset helpers for the PowerPC64 compiler optimizer.

Key contents:
- Active helpers include `bany`, `bnum`, `blsh`, and `Bconv`.
- `bany` tests whether any bit is set in a `Bits`.
- `bnum` returns the first set bit index and diagnoses empty input.
- `blsh` creates a one-bit `Bits`.
- `Bconv` formats bitsets as variable names or constant offsets using the optimizer’s `var[]` table.
- Older bitset union/intersection/not/equality/set helpers are present but commented out.

Filesystem relevance: indirect compiler optimizer utility code.
