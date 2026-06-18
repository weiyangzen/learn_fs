# sources/test-tools/stress-ng/test/test-attr-noreturn.c

Purpose: compile probe for compiler attribute support for `noreturn`, ensuring stress-ng can annotate functions, types, or objects with the corresponding optimization/diagnostic contract.

Important APIs/types/functions: `__attribute__` syntax or related compiler annotation forms; observed symbols: `__attribute__`, `noreturn_func`, `_exit`; includes: `<unistd.h>`, `<stdlib.h>`; macros: `NORETURN`.

Control flow: the file declares an annotated function/type/object and calls or references it from `main` when needed. Runtime behavior is incidental; the compile result is the detection signal.

State and persistence behavior: no persistent state. Any locals or static examples exist only to force the compiler to parse and type-check the attribute.

Dependencies and integration points: feeds stress-ng portability macros such as inline, noinline, noreturn, pure/const, packed, unused, weak, and returns-nonnull style annotations. Successful probes allow the main code to use stronger compiler hints without breaking other toolchains.

Risks and test signals: compilers may accept an attribute but ignore it, warn under different flags, or require placement on a specific declaration form. The meaningful signal is clean compilation with the configured warning policy.
