# File Research: sources/os/plan9/9front/sys/src/cmd/vl/span.c

This file assigns instruction PCs, resolves text size, classifies operands, and builds opcode lookup accelerators.

Key behavior:
- `span` walks the instruction stream assigning PCs, using `oplook` sizes, updating text symbol values, and adding workarounds for early MIPS 4000 page-boundary delay-slot bugs via `pagebug`.
- Repeats layout when large procedures require short branches to be expanded into branch-around-jump sequences.
- Optionally places string constants in text for debug mode.
- Computes `textsize`, `INITDAT`, and `etext`.
- `aclass` maps `Adr` operands into linker classes and computes `instoffset` for constants, extern/static/auto/param references, branches, and memory references.
- `oplook` selects and caches `Optab` entries, using exact ranges or precomputed `opcross` tables.
- `cmp`, `buildop`, and `buildrep` establish class compatibility, sorted opcode ranges, aliases, and fast replicated lookup tables.

Integration and risks:
- `pagebug` mutates branch-like instructions into NOP-plus-copy sequences before final layout.
- Operand classification reports undefined externals and may force symbols to `SDATA` to continue.
- `buildop` depends on fixed class enum assumptions.
