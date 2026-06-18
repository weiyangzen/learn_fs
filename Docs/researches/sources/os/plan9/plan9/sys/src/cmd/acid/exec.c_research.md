# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/exec.c

Acid AST evaluator, memory indirection, assignment, and function-call execution.

Key responsibilities:
- Reports interpreter errors and unwinds through `longjmp`.
- Executes AST nodes by dispatching through `expop`.
- Evaluates truthiness for integers, floats, strings, and lists.
- Converts floating values to integer words for memory stores.
- Reads target memory through libmach maps in many format sizes.
- Writes target memory for assignable indirection expressions.
- Handles function calls with parameter/local binding and return unwinding.

Dependencies:
- Uses `Node`, `Map`, libmach `get1/get2/get4/get8`, `put1/put2/put4/put8`, register accessors, and global interpreter state.
- Cooperates with expression operator implementations in `expr.c`.

Notable risks:
- Memory read/write format handling is central to debugger correctness.
- Error handling is nonlocal and stateful.
