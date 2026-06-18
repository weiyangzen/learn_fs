# File Research: sources/os/plan9/9front/sys/src/cmd/7c/machcap.c

Small target capability gate for the ARM64 backend. `machcap(Node *n)` reports whether a node operation is directly manageable by this machine backend.

Behavior:
- Returns true for null test probes.
- Accepts scalar integer/pointer/vlong multiply and assignment multiply when the node type is in `typechlv`.
- Accepts add/sub/and/or/xor and shifts when the left operand is in `typechlv`.
- Accepts casts, conditionals, comma/list/logical nodes, compound assignments, shifts, increments/decrements, comparisons, and signed negation for supported scalar classes.
- Explicitly rejects unsupported operations such as bitwise complement unless handled elsewhere.

Filesystem relevance: indirect compiler target capability metadata.
