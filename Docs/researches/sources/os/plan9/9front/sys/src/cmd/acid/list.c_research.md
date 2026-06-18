# File Research: sources/os/plan9/9front/sys/src/cmd/acid/list.c

Acid list construction, mutation, comparison, indexing, deletion, and stack-trace list materialization.

Key responsibilities:
- Builds list values from AST comma/list nodes.
- Computes list length, concatenates lists, appends values, indexes nth elements, deletes elements, and recursively compares lists.
- Builds two-element name/address variable lists.
- Builds lists of locals and parameters for stack frames using mach symbol metadata and frame pointer reads.
- `trlist()` appends stack trace frame records containing function address, caller PC, params, and locals.

Important behavior:
- Empty/out-of-range `nthelem()` returns an empty list, while delete beyond end is an error.
- `append()` allocates a new list element from the evaluated value’s `Store`.
- Stack trace records are nested lists suitable for Acid scripts to inspect.

Dependencies:
- Uses evaluator, list allocator, mach symbol APIs, map reads, and global `tracelist`.

Notable risks:
- `addlist()` mutates the left list in place.
- Delete returns a list with the target node unlinked but does not free it immediately; GC handles reachable/unreachable list cells.
