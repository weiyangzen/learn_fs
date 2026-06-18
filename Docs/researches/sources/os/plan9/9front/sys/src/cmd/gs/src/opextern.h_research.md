# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/opextern.h

Declares Ghostscript PostScript operator procedures that are intentionally referenced outside their defining source files and are available in all interpreter configurations.

The declarations cover fast/special operators used by `interp.c`, server-loop operators, save/restore hooks, Level 2 graphics state/page device helpers, VM-specific constructors, path construction operators, FunctionType 4 arithmetic/math/relational operators, CIE cache support, and miscellaneous shared operator entry points such as `ztoken`, `zwrite`, and `zclosefile`.

Dependencies are the interpreter context type `i_ctx_t` and `ref`, normally provided before or through surrounding operator headers.

This is cross-module interpreter API glue, not filesystem logic.
