# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/asm.c

PowerPC linker output writer for text, data, headers, symbols, and line tables.

Key responsibilities:
- Resolves the entry value from `INITENTRY`.
- Emits machine code by walking `Prog` instructions, consulting `oplook()` and `asmout()`, and checking phase errors.
- Handles text wrapping warnings and optional Virtex-4 boot jump injection.
- Emits data blocks from linker data initializers.
- Emits Plan 9 symbols and compressed line-number tables unless stripped.
- Writes headers for multiple `HEADTYPE` formats, including Plan 9, PEF-like, XCOFF-like, ELF, and boot-image variants.
- Provides endian-specific byte/word/long/vlong output helpers.
- Emits symbol table entries for globals, text symbols, files, frame sizes, autos, and params.

Dependencies:
- Uses linker globals and structures from `l.h`, `asmout.c`, `datap`, `textp`, dynamic linking helpers, and ELF helpers.

Notable risks:
- Output layout is controlled by `HEADTYPE`, `HEADR`, `INITTEXT`, `INITDAT`, and `dlm`.
- Data initialization performs overlap checks and relocation adjustments.
- Header constants encode historical platform formats.
