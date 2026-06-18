# File Research: sources/os/plan9/plan9/sys/src/cmd/6l/l.h

This is the central header for the amd64 linker `6l`. It imports Plan 9 headers, amd64 object constants, and ELF definitions, then declares linker data structures, constants, globals, and function prototypes.

Key structures are `Adr` for linker operands, `Prog` for linked instructions, `Auto` for automatic/history metadata, `Sym` for linker symbols, `Optab` for instruction encoding patterns, and `Movtab` for move encodings. Symbol types include text, data, bss, cross-reference, file, constant, undefined import, import, and export.

The header defines instruction encoding classes (`Y*`, `Z*`), prefix constants, REX bit flags, relocation bit packing, I/O buffers, global layout values (`HEADR`, `INITTEXT`, `INITDAT`, `INITRND`), symbol/hash tables, text/data lists, history state, dynamic module/import/export state, endian byte-order arrays, and output buffers.

Its prototypes cover object loading, archive/library handling, symbol lookup, patch/follow/layout passes, data output, ELF/Plan 9 assembly, dynamic relocation, profiling insertion, diagnostics, and formatting.

Filesystem relevance is build-system infrastructure: this is the linker contract for turning Plan 9 object files into bootable/runnable OS binaries.
