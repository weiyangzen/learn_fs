# File Research: sources/os/plan9/9front/sys/src/cmd/9c/machcap.c

Target capability predicate for the PowerPC64 C compiler backend.

Behavior:
- Returns true for null probe calls.
- Accepts integer/pointer/vlong multiply and assignment multiply when the node type is in `typechlv`.
- Accepts add/sub/and/or/xor/shifts when the left operand is an integer-like scalar.
- Accepts casts, conditionals, comma/list/logical nodes, compound assignments, shifts, increments/decrements, and all standard comparisons.
- Rejects operations not directly supported by this backend path, such as unary negation and complement here.

Filesystem relevance: indirect compiler target capability metadata.
