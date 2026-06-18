# File Research: sources/os/plan9/plan9/sys/src/cmd/cpp/test.c

Tiny macro-expansion test input.

It defines an empty function-like macro `M1`, a function-like macro `M2(A1)` that invokes its argument as a macro, then tests `M2(M1)` and `M2(P1)`. This exercises nested macro invocation and behavior when an argument names an undefined macro.
