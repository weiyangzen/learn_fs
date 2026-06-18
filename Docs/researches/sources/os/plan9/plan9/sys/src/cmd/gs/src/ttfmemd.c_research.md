# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfmemd.c

Purpose: Ghostscript GC structure descriptors for TrueType interpreter objects.

Key contents:
- Defines public descriptors for `TFace`, `TInstance`, `TExecution_Context`, `ttfFont`, and `ttfInterpreter`.
- Enumerates and relocates managed pointers in `TInstance`: face, definitions, code ranges, CVT, and storage.
- Enumerates and relocates many `TExecution_Context` pointers: current face, definitions, call stack, code ranges, storage, stack, glyph zones, twilight zones, and CVT.
- Enumerates and relocates `ttfFont` pointers: face, instance, execution context, interpreter.
- Defines pointer descriptor for `ttfInterpreter`: execution context, usage array, and memory object.

Dependencies: `ttmisc.h`, `ttfoutl.h`, `ttobjs.h`, `ttfmemd.h`, `gsstruct.h`.

Integration notes: required for Ghostscript’s garbage collector to trace and relocate FreeType-derived structures safely.

Risks: any pointer added to TrueType structs must be reflected here or GC relocation/tracing can become invalid.
