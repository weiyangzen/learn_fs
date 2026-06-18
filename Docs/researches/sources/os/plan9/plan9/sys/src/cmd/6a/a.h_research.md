# File Research: sources/os/plan9/plan9/sys/src/cmd/6a/a.h

This header defines the shared state and types for the amd64 assembler `6a`. It includes Plan 9 base headers, Bio I/O, and the amd64 object/instruction definitions from `../6c/6.out.h`.

Important types include `Sym` for assembler symbols, `Gen` and `Gen2` for encoded operands, `Io` for input streams, and `Hist` for source history records. `Gen` carries the operand type, symbol, offset, register index, scale, string constant, and floating constant data that later become Plan 9 object records.

The header declares assembler globals for debug flags, hash tables, include paths, input buffers, output file state, two-pass assembly state, source line tracking, and current PC. It also declares the assembler pipeline functions: lexical input, macro handling, include handling, parser entry, symbol setup, object output, history output, and platform wrappers.

Its filesystem-facing importance is mostly build-pipeline related: the assembler reads source files, include files, and emits `.6` object files. It also abstracts path handling and file creation across Plan 9, Unix, and Windows host environments.
