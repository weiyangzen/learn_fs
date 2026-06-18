# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttinterp.c

## Role

`ttinterp.c` is the TrueType bytecode interpreter used by this Ghostscript-derived TrueType scaler in the Plan 9 tree. It is FreeType-derived code with Aladdin/Ghostscript modifications. It executes font, CVT/prep, and glyph instruction streams over a `TExecution_Context`.

## Main Responsibilities

- Implements the interpreter dispatch loop in `RunIns(PExecution_Context exc)`.
- Defines opcode stack effects in `Pop_Push_Count`.
- Implements TrueType stack, flow-control, arithmetic, graphics-state, storage, CVT, outline, delta, function-definition, and instruction-definition opcodes.
- Selects optimized projection/movement/rounding/CVT access callbacks based on the current graphics state and pixel metrics.
- Maintains interpreter state through `CUR`, which maps to the passed execution context unless `TT_STATIC_INTERPRETER` is enabled.
- Uses `setjmp`/`longjmp` via `exc->trap` for disabled patented algorithms and error escape.

## Important Implementation Details

- The interpreter supports both indirect/reentrant and static/non-reentrant builds through macros. The normal path uses `PExecution_Context exc`.
- Axis-aligned projection and movement are fast-pathed through `Project_x`, `Project_y`, `Direct_Move_X`, and `Direct_Move_Y`.
- Non-axis projection routines `Project`, `Dual_Project`, and `Free_Project` are disabled with `THROW_PATENTED`, causing `TT_Err_Invalid_Engine`. This is a major behavioral limitation relative to a full TrueType interpreter.
- `RunIns` sets CVT handlers to stretched or normal variants depending on whether `x_ppem != y_ppem`.
- The opcode dispatch table maps all 256 bytecodes to named handlers, with unimplemented or custom opcodes routed through `Ins_UNKNOWN` so `IDEF` redefinitions can still be honored.
- Function definitions (`FDEF`) and instruction definitions (`IDEF`) are stored as code-range/start records in the execution context and later persisted back to the instance.
- The interpreter handles glyph zones (`pts`, `twilight`, `zp0`, `zp1`, `zp2`) and touch flags directly.
- Several compatibility comments describe undocumented TrueType behavior, including twilight-zone handling, Microsoft font behavior, phantom-point allowance in delta instructions, and out-of-range CVT reads being stubbed for a Ghostscript bug workaround.
- Debug builds allocate snapshots of point arrays around each instruction and log coordinate changes through the font debug hooks.

## Cross-File Relationships

- Public entry point is declared in `ttinterp.h`.
- Operates on structures and function pointer types from `ttobjs.h`.
- Uses table and scalar types from `tttables.h`, `tttypes.h`, and math helpers from `ttcalc.h`.
- Called by `Instance_Init`, `Instance_Reset`, and `Context_Run` in `ttobjs.c`.
- CVT, font program, and prep program byte arrays are loaded by `ttload.c`.

## Notable Risks / Review Notes

- Full TrueType hinting is intentionally incomplete because non-axis projection algorithms throw `TT_Err_Invalid_Engine`.
- Interpreter safety depends on table maxima and allocation sizes prepared by `ttobjs.c` and `ttload.c`.
- Many opcodes manipulate indexes from untrusted font bytecode; there are bounds checks throughout, but compatibility exceptions exist.
- `Ins_ALIGNPTS` appears to compute the projected y delta using `CUR.zp1.cur_x[p1]` in the second coordinate expression, which looks suspicious and may be a historical bug or typo.
- The file is legacy C with macro-heavy execution context access, making local reasoning about stack top, code range, and zone state delicate.
