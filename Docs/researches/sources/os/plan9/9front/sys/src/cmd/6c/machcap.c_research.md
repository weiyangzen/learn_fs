# File Research: sources/os/plan9/9front/sys/src/cmd/6c/machcap.c

- Role: Target capability predicate for the 6c amd64 backend.
- `machcap(Node *n)` returns whether a front-end tree operation is directly supported or useful for machine-specific lowering.
- Accepts arithmetic, bitwise, shift, multiply, assignment-op, increment/decrement, cast, conditional/logical/list/comma, and comparison nodes.
- Uses type class tables such as `typechl`, `typev`, `typechlv`, and `typechlpv` to restrict support to char/short/long/vlong/pointer-like integer classes where needed.
- `n == Z` returns true as a test capability.
- Practical effect: feeds front-end/codegen decisions about which expression trees can be handled by 6c target code rather than generic fallback.
