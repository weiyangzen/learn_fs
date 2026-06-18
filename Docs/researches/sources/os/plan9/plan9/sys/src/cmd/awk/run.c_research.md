# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/run.c

Tree-walking interpreter for awk.

Major runtime pieces:

- `run()` initializes standard I/O slots, executes the root program, then closes files.
- `execute()` dispatches AST nodes through `proctab[]`.
- `program()` runs `BEGIN`, main record loop, and `END`, with `setjmp`/`longjmp` for `exit`.
- Function calls use dynamic stack frames, copied scalar arguments, by-reference arrays, and a temporary return cell.
- Control flow uses special `Cell` values for `break`, `continue`, `next`, `nextfile`, `exit`, and `return`.

Implements awk semantics for arrays, `delete`, `in`, regex matches, booleans, comparisons, temporaries, indirect fields, `substr`, `index`, `sprintf`/`printf`, arithmetic, assignment, concatenation, pattern actions, range patterns, `split`, conditionals, loops, built-ins, printing, redirection, file cache/close/flush, `sub`, and `gsub`.

Notable design details include pooled temporary `Cell`s, cached redirection files/pipes keyed by filename, UTF-aware `substr`/`length`/`split("", ...)`, and special handling for empty-string substitutions.
