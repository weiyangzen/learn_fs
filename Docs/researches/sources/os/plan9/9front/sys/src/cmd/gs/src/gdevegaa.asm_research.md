# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevegaa.asm

## Role
`gdevegaa.asm` provides 16-bit x86 assembly helpers for the Ghostscript PC frame buffer driver, targeting Turbo C/large-code-model DOS-era builds.

## Entry Points
- `_vesa_call_set_page`: builds a VESA `4f05h` page-switch call and jumps through a caller-provided far procedure.
- `_memsetcol`: writes one byte per scanline down a column in frame-buffer memory.
- `_memsetrect`: fills rectangular byte regions, using byte loops for small widths and word stores for larger widths.
- `_memrwcol`: reads source bytes, rotates by a shift, optionally inverts, and writes one byte per destination scanline.
- `_memrwcol2`: similar to `_memrwcol`, but combines adjacent source bytes for shifted cross-byte output.

## Data Contract
- Uses a `rop_params` structure shared with C code. Offsets define destination pointer, destination raster, source pointer, source raster, byte width, height, shift, invert flag, and fill data.
- Preserves registers expected by Turbo C, especially `si` and `di` in routines that use them.

## Risks and Notes
- Highly platform-specific: 16-bit segmented x86, far pointers, DOS/Turbo C calling conventions, direct frame-buffer assumptions.
- No filesystem relevance. It is performance support for legacy display hardware operations.
