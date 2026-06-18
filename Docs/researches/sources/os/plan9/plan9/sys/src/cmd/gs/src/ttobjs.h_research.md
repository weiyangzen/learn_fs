# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttobjs.h

## Role

`ttobjs.h` defines the main object model and execution context contract for the FreeType-derived TrueType engine.

## Main Responsibilities

- Declares face, instance, execution context, and glyph pointer types.
- Defines `TGraphicsState`, `TCodeRange`, `TDefRecord`, `TCallRecord`, `TGlyph_Zone`, `TTransform`, `TSubglyph_Record`, and `TIns_Metrics`.
- Defines the three active TrueType code ranges:
  - font program
  - CVT/prep program
  - glyph instructions
- Defines interpreter callback function types for rounding, movement, projection, and CVT access.
- Defines `TExecution_Context`, the large mutable state object used by `RunIns`.
- Declares lifecycle, code-range, instance, face, and scaling functions implemented in `ttobjs.c`.

## Important Implementation Details

- `TGraphicsState` mirrors TrueType interpreter state: reference points, vectors, loop count, rounding, cut-ins, delta parameters, scan control, and zone pointer selectors.
- `TGlyph_Zone` stores original/current x/y coordinates, touch flags, contour endpoints, and point/contour counts.
- `TIns_Metrics` stores point size, resolution, ppem, scaling factors, non-square-pixel ratios, compensation values, and transform flags.
- `TExecution_Context` contains instruction stream state, function/instruction definitions, code ranges, storage, stack, rounding state, zones, graphics state, CVT, callback function pointers, `jmp_buf trap`, allocation capacities, and lock count.
- `EXEC_OPS`, `EXEC_OP`, `EXEC_ARGS`, and `EXEC_ARG` macros abstract indirect versus static interpreter builds.

## Cross-File Relationships

- Included by `ttinterp.h`, `ttinterp.c`, `ttobjs.c`, and `ttload.c`.
- Includes `tttables.h`, so face objects can embed `TMaxProfile`.
- The structs defined here are filled by `ttload.c`, managed by `ttobjs.c`, and mutated heavily by `ttinterp.c`.

## Notable Risks / Review Notes

- This header is the central ABI between loader, interpreter, and object manager. Field layout and macro changes would have broad effects.
- The execution context contains both borrowed pointers and owned buffers, so ownership is not obvious from the structure alone.
- The static/indirect interpreter macros make function signatures conditional at compile time.
