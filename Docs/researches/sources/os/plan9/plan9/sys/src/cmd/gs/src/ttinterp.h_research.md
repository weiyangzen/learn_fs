# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttinterp.h

## Role

`ttinterp.h` is the public header for the TrueType bytecode interpreter.

## Main Responsibilities

- Provides include guards and C++ linkage wrappers.
- Includes `ttcommon.h` and `ttobjs.h` so callers can reference `TT_Error` and `PExecution_Context`.
- Declares the interpreter entry point:
  - `TT_Error RunIns(PExecution_Context exc);`

## Cross-File Relationships

- Implemented by `ttinterp.c`.
- Used by `ttobjs.c`, where font, CVT, and glyph code ranges are selected and then executed.
- Depends on `TExecution_Context` from `ttobjs.h`.

## Notable Risks / Review Notes

- The header exposes only one function, so interpreter behavior is almost entirely governed by the mutable execution context contract.
- The comment says the TrueType instruction interpreter was cut out after FreeType, but this tree still contains a partial interpreter with patented projection paths disabled.
