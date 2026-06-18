# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttobjs.c

Object and execution-context manager for the Ghostscript TrueType interpreter subsystem.

Key points:
- Implements code-range management:
  - `Goto_CodeRange`
  - `Unset_CodeRange`
  - `Get_CodeRange`
  - `Set_CodeRange`
  - `Clear_CodeRange`
- Implements execution-context lifecycle:
  - `Context_Create` allocates/resizes call stack, operand stack, glyph point zone, twilight zone, and contour arrays.
  - `Context_Destroy` frees those arrays when the context lock reaches zero.
  - `Context_Load` copies instance state into the execution context.
  - `Context_Save` copies code-range/IDEF state back into the instance and clears context pointers to avoid stale references.
  - `Context_Run` prepares a glyph code range, resets glyph execution state, and calls `RunIns`.
- Implements default graphics state as `Default_GraphicsState`.
- Implements instance lifecycle:
  - `Instance_Create` allocates function definitions, instruction definitions, scaled CVT, and storage arrays.
  - `Instance_Destroy` frees instance-owned interpreter data.
  - `Instance_Init` runs the font program (`fpgm`) once against a fresh instance.
  - `Instance_Reset` computes ppem/scaling/ratio state, scales the CVT, resets storage and twilight points, and runs the prep/CVT program.
- Implements face lifecycle:
  - `Face_Create` loads only maxp, CVT, and programs in this adapted build.
  - `Face_Destroy` frees CVT and program buffers.
- Provides `Scale_X` and `Scale_Y` helpers for FUnit-to-26.6 scaling.
- Uses allocation macros that reuse existing arrays when already large enough and grow them only as needed.
- Adds several Ghostscript-specific robustness changes:
  - shared context reuse and locking
  - avoiding full context buffer release on failed resize
  - extra stack headroom
  - minimum 50 FDEF slots for a known font bug
  - failure handling for low-memory cleanup paths.

Dependencies and interactions:
- Includes `ttmisc.h`, `ttfoutl.h`, `ttobjs.h`, `ttcalc.h`, `ttload.h`, and `ttinterp.h`.
- Uses `ttfMemory` for all allocation/free operations.
- Calls `Load_TrueType_MaxProfile`, `Load_TrueType_CVT`, and `Load_TrueType_Programs`.
- Calls `RunIns` to execute font, prep, and glyph programs.
- Reads font table metadata through the `PFace`/`ttfFont` structures.

Research relevance:
- This file owns the interpreter runtime state model: how face-global data, size-specific instance data, and transient glyph execution data move between structures before and after bytecode execution.
