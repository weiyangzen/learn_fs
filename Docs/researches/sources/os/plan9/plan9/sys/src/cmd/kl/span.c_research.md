# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/span.c

Read fully: 524 lines, 10152 bytes. SHA-256 prefix: `6a16438fc5ae21db`.

This file assigns final PCs, classifies operands, and builds optimized opcode lookup ranges.

Important routines:
- `span()` walks the final instruction list from `INITTEXT`, assigns `pc`, consults `oplook()` for size, updates text symbol values, rounds text size, and computes `INITDAT`.
- `xdefine()` defines linker-generated symbols if not already defined.
- `regoff()` and `aclass()` compute effective offsets and classify operands into constants, registers, branches, stack/global memory forms, extern/static/auto/param addressing, ASI, and special registers.
- `oplook()` matches a `Prog` to a cached `Optab` row using operand classes and comparison matrix `xcmp`.
- `cmp()`, `ocmp()`, and `buildop()` build compatibility and sorted opcode ranges, also aliasing related opcodes to shared table ranges.

Integration: used by scheduling, span, and assembly. `aclass()` depends on symbol types and layout values from `dodata()` and text values from `patch()`/`span()`.

Risk notes: there is a commented-out alternative for external constants and an unconditional `return C_LCON` for one case, indicating a known historical workaround. Cached operand classes can become stale if operands are mutated later.
