# File Research: sources/os/plan9/9front/sys/src/cmd/1l/span.c

Purpose: linker span/symbol-table support for the 68000-family `1l` linker. It assigns final text PCs, resolves branch instruction sizes, computes symbol/line/stack-map output streams, and defines special linker symbols.

Key behavior:
- `span()` iteratively assigns instruction PCs from `INITTEXT`, expands branches when displacements outgrow short forms, rewrites `AADJSP` into concrete stack adjustment instructions, aligns `INITDAT`, and defines `etext` and `a6base`.
- `andsize()` computes operand extension-word size from addressing mode, symbol class, displacement range, constants, FPU constants, special registers, and A6-relative data addressing.
- `asmsym()` emits text, data, bss, file, auto, and parameter symbols via `putsymb()`.
- `asmsp()` emits compressed PC-to-stack-offset deltas; `asmlc()` emits compressed PC-to-line-number deltas.
- Uses globals from `l.h`: `firstp`, `textp`, `optab`, `mmsize`, `INITTEXT`, `INITDAT`, `A6OFFSET`, debug flags, and output macros.

Research notes:
- The branch sizing loop is bounded at 60 passes and treats zero displacement specially by forcing a 4-byte branch form.
- Static/external non-text data may use compact A6-relative forms when within signed 16-bit range.
- Symbol output supports Plan 9 path-encoded `z`/`Z` file symbols.
