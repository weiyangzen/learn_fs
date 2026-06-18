# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttobjs.h

Core object, graphics-state, code-range, glyph-zone, metrics, face, instance, and execution-context definitions for the TrueType subsystem.

Key points:
- Documents FreeType’s four object categories:
  - face
  - instance
  - execution context
  - glyph
- Declares opaque/forward types for `TFace`, `TInstance`, `TExecution_Context`, and `TGlyph`.
- Defines `TGraphicsState` with reference points, projection/dual/freedom vectors, loop, minimum distance, round state, auto-flip, cut-ins, delta parameters, instruction/scan controls, scan type, and zone pointer selectors.
- Defines three active code ranges:
  - `TT_CodeRange_Font`
  - `TT_CodeRange_Cvt`
  - `TT_CodeRange_Glyph`
- Defines `TCodeRange`, `TDefRecord`, and `TCallRecord` for bytecode execution.
- Defines `TGlyph_Zone` with original/current x/y coordinate arrays, touch flags, contour endpoints, and counts.
- Defines execution macro families for indirect and static interpreter modes:
  - `EXEC_OPS`
  - `EXEC_OP`
  - `EXEC_ARGS`
  - `EXEC_ARG`
- Defines interpreter callback function pointer types:
  - rounding
  - moving
  - projection
  - CVT read/write/move
- Defines composite glyph support structures:
  - `TTransform`
  - `TSubglyph_Record`
- Contains an extended note explaining non-square-pixel CVT scaling and ratio computation.
- Defines `TIns_Metrics` for point size, resolutions, ppem, scaling ratios, compensation values, rotation, and stretching.
- Defines `TFace` with reader/font pointers, maxp data, program buffers, CVT, and derived maxima.
- Defines `TInstance` with face pointer, validity flag, metrics, FDEF/IDEF arrays, IDEF opcode map, code ranges, graphics state, scaled CVT, and storage.
- Defines `TExecution_Context` with current instruction state, code range, stacks, function/instruction definitions, glyph zones, graphics state, metrics, CVT/storage pointers, function pointers, `jmp_buf trap`, allocation maxima, and lock.
- Declares lifecycle and helper functions implemented in `ttobjs.c`.

Dependencies and interactions:
- Includes `ttcommon.h`, `tttypes.h`, `tttables.h`, and `<setjmp.h>`.
- Supplies the structures consumed heavily by `ttinterp.c`, `ttobjs.c`, and `ttload.c`.

Research relevance:
- This is the structural contract for the entire TrueType interpreter runtime. Most behavior in `ttinterp.c` is direct mutation of fields declared here.
