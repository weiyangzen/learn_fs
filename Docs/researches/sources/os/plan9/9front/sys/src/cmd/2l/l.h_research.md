# File Research: sources/os/plan9/9front/sys/src/cmd/2l/l.h

Purpose: shared declarations and global state for the 68020 linker `2l`.

Key contents:
- Includes Plan 9 headers, shared `2.out.h`, and common compatibility declarations.
- Defines linker `Adr`, `Prog`, `Auto`, `Sym`, and `Optab` structures.
- `Adr` stores offset/displacement, string constants, branch condition pointer, IEEE constants, auto/symbol references, bit-field width, and scale.
- `Prog` stores source/destination operands, stack offset/forward pointer, link, branch target `pcond`, final PC, line, opcode, and span marks.
- Defines symbol classes: `STEXT`, `SDATA`, `SBSS`, `SDATA1`, `SXREF`, `SAUTO`, `SPARAM`, `SFILE`.
- Declares output layout globals (`HEADR`, `HEADTYPE`, `INITTEXT`, `INITDAT`, `INITRND`, sizes, buffers), symbol/library state, program lists, history state, byte-order tables, and address-mode lookup tables.
- Declares linker phases: object loading, autolib loading, patching/following/data layout/stack offsets/span/output, instruction encoding, data block writing, symbol maps, diagnostics, lookup, profiling injection, and float conversion.

Research notes:
- `CPUT` writes to a buffered output array and flushes through `cflush()` when full.
- `TNAME` resolves current text symbol for diagnostics.
- `A6OFFSET` is the base used for compact A6-relative data addressing.
