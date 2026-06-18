# File Research: sources/os/plan9/9front/sys/src/cmd/9l/span.c

This file computes final text addresses, classifies operands, selects optab entries, builds opcode lookup ranges, expands too-distant short branches, and serializes dynamic relocation metadata.

Key routines:
- `span` assigns `pc` values, handles explicit `TEXT` origins, detects large procedures, expands out-of-range conditional branches by inserting branch-around sequences, rounds text size, sets `etext`, and computes `INITDAT`.
- `xdefine` defines linker-generated symbols if not already defined.
- `vregoff` and `regoff` classify operands and return computed offsets.
- `isint32` and `isuint32` test constant ranges.
- `aclass` maps `Adr` operands to `C_*` classes and computes `instoffset` for extern/static/auto/param/constant/branch forms.
- `oplook` matches an instruction against sorted optab ranges and caches the selected optab index.
- `cmp` defines class-subsumption rules used by optab matching.
- `ocmp` sorts optab entries.
- `buildop` constructs `xcmp` compatibility tables, sorts `optab`, creates `oprange`, and aliases many opcode variants to shared pattern ranges.
- `dynreloc` records sorted dynamic relocation entries.
- `asmdyn` writes import and relocation tables after the main image.

Important interactions:
- Uses `optab.c` patterns and `asmout.c` encoder cases.
- Called after `noops`; its resulting `pc`, `textsize`, and `INITDAT` are consumed by `asm.c`.
- In DLM mode, `aclass` classifies symbol references as relocatable addresses and `dynreloc` records them.

Research notes:
- Short conditional branch expansion is iterative because inserting branches changes later PCs.
- Operand classes encode both addressing mode and offset range, making optab matching compact.
- Dynamic relocation records are delta-compressed when written by `asmdyn`.
