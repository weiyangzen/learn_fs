# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttinterp.h

Public header for the TrueType bytecode interpreter.

Key points:
- Carries the same FreeType/Ghostscript provenance comments as `ttinterp.c`.
- Includes `ttcommon.h` and `ttobjs.h`.
- Declares the single interpreter entry point:
  - `TT_Error RunIns(PExecution_Context exc)`
- Wraps declarations in `extern "C"` for C++ consumers.
- Has standard include guards.

Dependencies and interactions:
- `PExecution_Context` comes from `ttobjs.h`.
- Used by `ttobjs.c` to run font, CVT, and glyph programs.

Research relevance:
- This is the narrow public contract for the interpreter: clients provide a prepared execution context and receive a TrueType error code.
