# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfmemd.c

GC memory structure descriptors for TrueType interpreter objects.

Key behavior:
- Defines public structure descriptors for:
  - `TFace`
  - `TInstance`
  - `TExecution_Context`
  - `ttfFont`
  - `ttfInterpreter`
- `TFace` descriptor traces reader, font, font program, CVT program, and CVT pointers.
- `TInstance` custom enum/reloc traces face, function/instruction definitions, code range bases, CVT, and storage.
- `TExecution_Context` custom enum/reloc traces current face, definitions, call stack, code ranges, storage, stack, glyph point arrays, twilight point arrays, and CVT.
- Comments mark some fields as local or never used and intentionally not GC-traced.
- `ttfFont` descriptor traces face, instance, execution context, and interpreter pointer.
- `ttfInterpreter` descriptor traces execution context, subglyph usage buffer, and memory wrapper.

Dependencies and interactions:
- Includes `ttmisc.h`, `ttfoutl.h`, `ttobjs.h`, `ttfmemd.h`, and `gsstruct.h`.
- Used by `ttfmain.c` allocations through `ttfMemory`.

Research relevance:
- Essential for keeping FreeType-derived TrueType data safe under Ghostscript’s moving GC.
