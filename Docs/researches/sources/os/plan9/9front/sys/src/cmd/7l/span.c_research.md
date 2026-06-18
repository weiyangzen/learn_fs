# File Research: sources/os/plan9/9front/sys/src/cmd/7l/span.c

This is the span and instruction-selection support for the Plan 9/9front `7l` linker, covering ARM64 text layout, literal pool placement, operand classification, and opcode-table lookup.

Key responsibilities:
- Assigns final `pc` values to linked `Prog` instructions in `span()`, accounting for alignment, instruction widths from `oplook()`, function boundaries, and `etext`/`textsize`.
- Maintains ARM64 literal pools through `addpool()`, `checkpool()`, and `flushpool()`, inserting branch-over-pool sequences when PC-relative literal references approach range limits.
- Classifies operands in `aclass()` into linker-internal classes such as register, stack/auto offset classes, add-immediate constants, bitmask constants, branch classes, external symbols, and large constants.
- Implements constant-shape recognizers for ARM64 encodings: add immediates, logical bitmask immediates, MOVK/MOVN-compatible fields, and scaled load/store offsets.
- Builds and caches opcode lookup ranges in `buildop()`, mapping many instruction aliases to shared optab entries.

Integration points:
- Depends on `l.h` definitions for `Prog`, `Adr`, `Sym`, `Optab`, opcode/class constants, and linker global state.
- `oplook()` is central to both span-time sizing and later machine-code emission.
- `aclass()` sets global `instoffset`, so callers rely on its side effect as well as its return class.

Risks and invariants:
- Literal pool range logic is architecture-sensitive; comments note an unresolved limitation that old literal values should remain referenceable until actually out of range.
- `findmask64()` contains a debug `print()` when a mask is found, which is unusual in production compiler/linker code.
- Incorrect operand class widening in `cmp()` or alias setup in `buildop()` can silently select invalid encodings.
