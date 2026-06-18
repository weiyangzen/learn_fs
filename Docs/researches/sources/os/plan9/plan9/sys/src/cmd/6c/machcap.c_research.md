# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/machcap.c

`machcap` reports whether the amd64 backend can handle a given compiler tree operation directly. It returns true for many integer and pointer arithmetic operations, casts, conditionals, logical operators, assignments, compound assignments, shifts, increment/decrement, comparisons, and supported multiply forms.

It treats small integer and vlong multiply as supported and permits common unary/binary operations on character, short, long, pointer, and vlong categories. Unsupported operations return false, allowing generic compiler code to avoid target-specific lowering paths.

Filesystem relevance is indirect: this is a target capability gate in the compiler. It affects which expressions from OS/filesystem code can be lowered directly by the amd64 backend versus requiring generic transformations.
