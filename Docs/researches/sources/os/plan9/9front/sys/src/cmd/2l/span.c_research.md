# File Research: sources/os/plan9/9front/sys/src/cmd/2l/span.c

This file computes final instruction sizes and PCs for `2l`, defines key linker symbols, and emits symbol, stack-pointer, and line-number tables.

Key routines:
- `span()` converts pseudo `AADJSP` instructions into real stack-pointer adjustments, iteratively sizes instructions and branches until `textsize` stabilizes, aligns data start with `INITRND`, defines `etext` and `a6base`, then writes final text symbol PCs.
- `xdefine()` defines a linker symbol only when undefined or suitable for STEXT zero replacement.
- `andsize()` computes extra bytes required by an addressing mode, including indexed modes, text/static/extern references, stack/autos/params, constants, FP constants, special registers, and long displacements.
- `putsymb()` writes one symbol-table entry, with special handling for file symbols encoded as `Z`/`z`.
- `asmsym()` emits data, BSS, file, text, auto, and param symbols in Plan 9 symbol-table format.
- `asmsp()` encodes stack-pointer delta tables in compact bytecode form.
- `asmlc()` encodes line-number delta tables similarly.

Dependencies and interactions:
- Consumes `firstp`, `textp`, `optab`, `mmsize`, `simple`, and layout constants such as `INITTEXT`, `INITDAT`, `A6OFFSET`, and `INITRND`.
- Follows work done by `pass.c`: branch targets and `stkoff` are expected to be established before symbol/debug table emission.

Research relevance:
- This is the final sizing and debug-metadata pass for `2l`. It determines final PCs, branch encodings, text/data split, and symbol records.

Risk notes:
- Branch-size iteration has a hard loop limit of 60; size oscillations or bad branch marks abort the link.
- `andsize()` is architecture-encoding sensitive; small mistakes can desynchronize PC assignment from emitted code.
- Stack and line tables assume a minimum instruction location counter quantum of 2 bytes.
