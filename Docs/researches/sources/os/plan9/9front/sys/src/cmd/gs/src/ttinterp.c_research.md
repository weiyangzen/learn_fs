# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttinterp.c

FreeType-derived TrueType bytecode interpreter adapted for Ghostscript.

Key points:
- Implements `RunIns(PExecution_Context exc)`, the main TrueType instruction execution loop.
- Supports both static and indirect interpreter builds through `TT_STATIC_INTERPRETER`, with the indirect/re-entrant mode as the normal path.
- Uses `Pop_Push_Count[512]` to preflight stack pops/pushes for each opcode before dispatch.
- Computes variable instruction lengths for `NPUSHB`, `NPUSHW`, `PUSHB[]`, and `PUSHW[]`, and validates instruction-pointer bounds.
- Maintains code ranges for font program, CVT/prep program, and glyph instruction program.
- Provides stack, flow-control, logical, arithmetic, storage, CVT, graphics-state, outline, delta, and miscellaneous instruction handlers.
- Implements function definitions and calls:
  - `FDEF`, `ENDF`
  - `CALL`, `LOOPCALL`
  - `IDEF` and redirected unknown-opcode execution through `IDefPtr`.
- Implements vector setup and graphics-state changes:
  - projection/freedom/dual vectors
  - zone pointers
  - reference points
  - rounding mode
  - scan/instruction control
  - delta base and shift
- Implements point movement and interpolation instructions over normal and twilight zones:
  - `MDAP`, `MIAP`, `MDRP`, `MIRP`
  - `SHP`, `SHC`, `SHZ`, `SHPIX`
  - `IUP`, `IP`, `ALIGNRP`, `ALIGNPTS`, `ISECT`
  - point on/off-curve flag flipping
- Handles CVT access with separate square-pixel and stretched non-square-pixel routines.
- Uses `setjmp`/`longjmp` through `exc->trap` for hard interpreter exits.
- Ghostscript’s copy disables patent-sensitive projection implementations with `THROW_PATENTED`; generic `Project`, `Dual_Project`, and `Free_Project` throw `TT_Err_Invalid_Engine`, while axis-aligned `Project_x`/`Project_y` remain usable.
- Contains compatibility/workaround comments for real fonts and bugs, including out-of-range CVT read tolerance, extra stack space assumptions, phantom-point delta allowance, and twilight-zone behavior.
- Debug builds can print instruction traces, repaint, and compare point coordinate arrays before/after each instruction.

Dependencies and interactions:
- Includes `ttmisc.h`, `ttfoutl.h`, `tttypes.h`, `ttcalc.h`, `ttinterp.h`, and `ttfinp.h`.
- Uses execution context, graphics state, glyph zones, CVT/storage arrays, function records, and call records defined in `ttobjs.h`.
- Uses fixed-point and 64-bit helper macros from `ttcalc.h`.
- Called by `Instance_Init`, `Instance_Reset`, and `Context_Run` in `ttobjs.c`.
- Reads face/font debug callbacks through `current_face->font`.

Research relevance:
- This is the central TrueType hinting bytecode engine in this Ghostscript source tree. Its error paths, stack bounds, code-range transitions, CVT behavior, and patented-algorithm disablement determine how embedded TrueType instructions affect glyph loading and rendering.
