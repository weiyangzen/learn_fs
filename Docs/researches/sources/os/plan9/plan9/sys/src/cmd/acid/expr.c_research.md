# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/expr.c

Expression operator implementations for the Acid language.

Key responsibilities:
- Determines formatted value sizes.
- Checks lvalue validity.
- Evaluates list sequencing, forced evaluation, casts, memory/code indirection, stack-frame lookup, indexing, append/delete/head/tail, constants, names, complex construction, assignment, arithmetic, shifts, comparisons, equality, bitwise/logical operators, unary not, pre/post increment/decrement, function calls, formatting, and `what`.
- Handles mixed integer/float/string/list cases where Acid defines them.
- Dispatches complex field access through `odot`.

Dependencies:
- Uses global `expop`, `Node`, `List`, `Value`, libmach maps, `indir`, `windir`, `call`, `append`, `delete`, `nthelem`, `stradd`, and string/list helpers.

Notable risks:
- Type coercion behavior is manual and old-debugger-specific.
- Many operators mutate `Node` results in place; correctness depends on exact `type`, `fmt`, and value fields.
