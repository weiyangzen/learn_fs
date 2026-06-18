# File Research: sources/os/plan9/9front/sys/src/cmd/kl/asm.c

Assembler/output backend for the SPARC linker `kl`. `asmb` writes text, data, symbols, line tables, and executable headers for supported `HEADTYPE`s. It verifies PC phase, calls `oplook`/`asmout` for instruction encoding, emits initialized data blocks, serializes symbols and source line tables, and writes final headers with text/data/bss/symbol sizes and entry value.

`datblk` materializes initialized data with endian conversion and relocation-like symbol value resolution. `asmout` is the main lowering matrix from `Prog`/`Optab` classes to SPARC machine words, including immediates, large constants, branches, calls, traps, FP loads/stores/arithmetic, div/mod expansion, and annulled delay-slot opportunities. `opcode` maps internal `A*` opcodes to SPARC encodings.
