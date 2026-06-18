# File Research: sources/os/plan9/9front/sys/src/cmd/1l/l.h

Primary header for the Plan 9 `1l` 68000 linker.

Key contents:
- Includes Plan 9 libc/Bio, 68000 object definitions from `../2c/2.out.h`, and compatibility declarations.
- Defines linker data structures: `Adr`, `Prog`, `Auto`, `Sym`, and `Optab`.
- Defines symbol classes such as `STEXT`, `SDATA`, `SBSS`, `SDATA1`, `SXREF`, `SAUTO`, `SPARAM`, and `SFILE`.
- Declares global output buffers, section sizes, header parameters, symbol tables, text/data lists, library/autolib state, endian maps, and special/simple addressing tables.
- Declares linker passes: object loading, library loading, branch patching, layout, data allocation, stack offset rewriting, span calculation, assembly, symbol/line/reloc output, diagnostics, and helpers.
- Defines `CPUT` output-buffer macro and formatting pragmas.

Role in system:
- Shared contract for all `cmd/1l` linker source files.
