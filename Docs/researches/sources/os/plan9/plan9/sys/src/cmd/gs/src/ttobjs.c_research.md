# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttobjs.c

## Role

`ttobjs.c` manages TrueType face, instance, and execution-context lifecycle for this scaler. It is the glue between loaded font tables, scaled instance metrics, and bytecode execution.

## Main Responsibilities

- Manages code ranges:
  - `Goto_CodeRange`
  - `Unset_CodeRange`
  - `Get_CodeRange`
  - `Set_CodeRange`
  - `Clear_CodeRange`
- Creates, grows, loads, saves, and destroys execution contexts.
- Creates, initializes, resets, and destroys font instances.
- Creates and destroys face-level data.
- Provides scaling helpers `Scale_X` and `Scale_Y`.
- Defines `Default_GraphicsState`.

## Important Implementation Details

- `Context_Create` is an adjust/grow operation rather than a pure constructor. It allocates or expands shared buffers for stacks, glyph point zones, twilight zone, and contours.
- Execution contexts are reference-counted with `lock`; `Context_Destroy` frees buffers only when the lock count drops to zero.
- `Context_Load` copies instance state into the execution context before running bytecode. `Context_Save` persists definitions, code ranges, CVT/storage pointers, and IDEF mapping back to the instance.
- `Context_Run` prepares glyph code execution by selecting `TT_CodeRange_Glyph`, resetting zone pointers, graphics-state vectors, stack top, and call stack, then calling `RunIns`.
- `Instance_Create` allocates function definitions, instruction definitions, scaled CVT storage, and TrueType storage. It enforces a maximum of 255 instruction definitions and raises the FDEF table to at least 50 entries for a Ghostscript bug workaround.
- `Instance_Init` executes the font program (`fpgm`) with neutral metrics and disabled CVT/glyph code ranges.
- `Instance_Reset` recomputes scaling for a ppem/transform, scales face CVT values into the instance CVT, clears storage and twilight points, and executes the prep/CVT program.
- `Face_Create` currently loads only max profile, CVT, and programs; other TrueType table loads are commented out.
- Memory management uses the `ttfMemory` allocator through local `FREE` and `ALLOC_ARRAY` macros.

## Cross-File Relationships

- Calls `RunIns` from `ttinterp.c`.
- Uses loader functions from `ttload.c`.
- Implements declarations from `ttobjs.h`.
- Uses table structures from `tttables.h`, especially `TMaxProfile`.
- Relies on `ttfMemory`, `ttfFont`, and `ttfReader` types from surrounding Ghostscript TrueType code.

## Notable Risks / Review Notes

- Shared-context reuse makes ownership subtle. Failed allocation intentionally does not destroy existing shared buffers.
- `Context_Destroy` returns `TT_Err_Out_Of_Memory` if `current_face` is missing, even during cleanup. The comment explains this as a high-level device close edge case.
- `Face_Create` omits many standard TrueType tables, implying this component is a specialized hinting/program subset rather than a full standalone TrueType loader.
- Instance validity depends on successful prep execution; invalid ppem values return `TT_Err_Invalid_PPem`.
