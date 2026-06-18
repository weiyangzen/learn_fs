# File Research: sources/os/plan9/9front/sys/src/cmd/7l/asmout.c

ARM64 instruction encoder for the 9front linker. It converts linked `Prog` instructions plus `Optab` classifications into one or more 32-bit machine instructions.

Key structure:
- Defines many ARM64 encoding macros for register fields, data-processing forms, branches, system operations, load/store forms, floating-point operations, ADR/ADRP, and logical shifts.
- `asmout` is the central switch over `o->type`; it covers pseudo-ops, arithmetic/logical forms, immediates, branches, shifts, multiply/divide/remainder, conditional select/compare, loads/stores, pair loads/stores, wide moves, system registers, barriers/hints, bitfield aliases, floating-point arithmetic/compare/convert, exclusive atomics, ADR/ADRP, jump tables, relocating memory operations, and huge-offset fallbacks.
- Emits instruction words according to `o->size` through `lputl`, with debug assembly dumps when requested.

Major helper functions:
- `oprrr` maps register-register, multiply, conditional, crypto, floating, and conversion opcodes to base encodings.
- `opirr` maps immediate, logical-immediate, branch-test, move-wide, system, barrier, and bitfield immediate opcodes.
- `opbit`, `opxrrr`, `opimm`, `opbra`, `opbrr`, `op0`, `opload`, and `opstore` handle specialized opcode families.
- `brdist` computes and validates PC-relative branch distances, including relocation handling for unresolved dynamic targets.
- `olsr12u`, `olsr9s`, `opldr12`, `opldr9`, `opstr12`, `opstr9`, `opldrpp`, and `olsxrr` encode load/store addressing modes.
- `omovlit` emits literal-pool loads or immediate materialization through add-from-zero.
- `opbfm` and `opextr` encode bitfield/extract forms and validate bit ranges.
- `movesize` returns log2 byte widths for load/store offset scaling.

Important details:
- Large memory offsets are decomposed through `REGTMP` materialization plus register-offset load/store forms.
- `ACASE` emits an inline jump-table dispatch sequence; `ABCASE` entries are relative to the preceding `ACASE`.
- DLM relocations are emitted for address constants and branch/case targets where required.
- Floating constants are accepted only when `chipfloat` or zero-immediate rules can encode them.

Filesystem relevance: indirect linker machine-code backend.
