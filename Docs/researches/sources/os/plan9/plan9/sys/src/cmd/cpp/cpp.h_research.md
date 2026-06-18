# File Research: sources/os/plan9/plan9/sys/src/cmd/cpp/cpp.h

Shared private header for the Plan 9 C preprocessor.

It defines buffer and nesting limits, token type and keyword enums, macro flags, sentinel bytes, token/source/name-list/include-list structs, quick macro lookup bitsets, and all cross-module function prototypes. `Tokenrow` is the central mutable token sequence abstraction; `Source` forms the include/string-source stack; `Nlist` stores preprocessor keywords and macro definitions.

The header also exposes global state such as `cursource`, `incdepth`, `ifdepth`, `skipping`, include lists, current time string, and output pointer.
