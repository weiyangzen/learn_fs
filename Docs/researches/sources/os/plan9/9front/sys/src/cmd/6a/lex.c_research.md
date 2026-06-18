# File Research: sources/os/plan9/9front/sys/src/cmd/6a/lex.c

This file implements `6a` startup, keyword/register initialization, two-pass assembly orchestration, object-record serialization, source-history emission, and inclusion of shared lexer/macro bodies.

Key elements:
- `main()` sets architecture identity (`6`, `amd64`), initializes symbols, parses flags, supports `-o`, `-D`, and `-I`, and can assemble multiple files in parallel using `NPROC`.
- `assemble()` derives output filename, configures include paths, opens output, runs parser pass 1, then emits history and runs parser pass 2.
- `itab[]` maps names to token classes and opcode/register/address values. It includes:
  - SP/SB/FP/PC pseudo-registers,
  - byte, word, long, MMX, XMM, segment, control/debug/test registers,
  - core x86 opcodes,
  - amd64 opcodes,
  - FPU opcodes,
  - conditional jumps and conditional moves,
  - SSE/MMX/3DNow-style media opcodes,
  - instruction synonyms.
- `cinit()` initializes `nullgen`, symbol hash, predefined symbols/opcodes, and current working directory.
- `checkscale()` enforces x86 index scales of 1, 2, 4, or 8.
- `cclean()` emits `AEND` and flushes output.
- `zname()` writes `ANAME` records.
- `zaddr()` writes compact operand encodings with flags for type, index, offset, float, symbol, string, and 64-bit offset.
- `outcode()` serializes instructions in pass 2 and maintains object symbol cache slots.
- `outhist()` serializes source path history as `ANAME` and `AHISTORY` records.
- Includes `../cc/lexbody`, `../cc/macbody`, and `../cc/compat`.

Dependencies and integration:
- Parser actions from `a.y` call `outcode()`.
- Object format constants and opcode IDs come from `6.out.h`.

Notable behavior:
- `outcode()` increments `pc` for most instructions but not `AGLOBL`, `ADATA`, or `AMODE`.
- Symbol cache slots wrap within `NSYM`; if source and destination choose the same cache slot, serialization restarts.
- On Plan 9, default include path is `/<arch>/include`; environment `INCLUDE` can override/add paths.
- Multi-file assembly is disabled on Windows.

Research notes:
- This file is both lexer initialization and object writer; the actual lexical scanner and macro implementation are included from shared compiler sources.
