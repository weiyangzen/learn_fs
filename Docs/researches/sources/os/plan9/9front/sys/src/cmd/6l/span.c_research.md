# File Research: sources/os/plan9/9front/sys/src/cmd/6l/span.c

- Role: Final instruction sizing, PC assignment, operand classification, amd64 byte emission, symbol/line table emission, and dynamic relocation output for 6l.
- `span()` iteratively encodes instructions until branch sizes stabilize, updates `INITDAT` alignment, defines `etext`, and writes final text symbol PCs.
- `oclass()` classifies operands into `Y*` classes used by `optab[]`, including immediates, registers, memory, branches, constants, special registers, XMM/MMX/x87 registers, and mode-specific register validity.
- Address encoding functions `asmidx()`, `asmandsz()`, `asmand()`, and `asmando()` emit ModRM/SIB/displacement bytes, handle REX bits, symbol relocation via `vaddr()`, and special SP/BP/R12/R13 addressing cases.
- `doasm()` interprets `Optab` patterns and `Z*` templates to emit instruction bytes, branch displacements, immediates, media op escapes, MOV special cases from `ymovtab`, byte-register rewrites for non-64-bit modes, and data pseudo bytes.
- `asmins()` wraps `doasm()` and inserts the REX prefix in the correct position after legacy prefixes and before opcode escape bytes.
- `asmsym()` and `putsymb()` emit Plan 9 symbol tables, including text, data, bss, constants, file history, frames, autos, and params.
- `asmlc()` emits compressed line-number tables.
- Dynamic relocation support is implemented by `dynreloc()`, relocation-array growth, and `asmdyn()` import/relocation table serialization.
