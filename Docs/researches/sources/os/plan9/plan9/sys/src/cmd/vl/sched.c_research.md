# File Research: sources/os/plan9/plan9/sys/src/cmd/vl/sched.c

MIPS instruction scheduler for bounded basic blocks.

Key responsibilities:
- Builds a side array of scheduling records containing copied `Prog`, register/memory/condition dependencies, memory offsets, sizes, and compound-instruction flags.
- Classifies instructions through `regsused()`, including integer regs, floating regs, HI/LO, FCR/MCR, SB/SP/general memory, loads, branches, and floating compares.
- Reorders loads and independent filler instructions to cover load, branch, and floating compare delay slots.
- Inserts nops when no legal filler is available.
- Adds extra nops for HI/LO use followed by HI/LO set.
- Writes scheduled instructions back into the original linked list.

Important behavior:
- Memory dependencies distinguish general memory, SB-relative memory, and SP-relative memory, allowing non-overlapping SB/SP references to pass each other.
- Compound instructions and non-4-byte encodings are kept more conservatively.
- Register zero is masked out as a set target.

Risks:
- Correctness depends on exact `aclass()` and `oplook()` classifications.
- Memory overlap is size/offset based and conservative for unknown/global memory.
