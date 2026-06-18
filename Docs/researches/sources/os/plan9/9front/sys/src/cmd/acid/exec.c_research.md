# File Research: sources/os/plan9/9front/sys/src/cmd/acid/exec.c

Statement execution, function call frames, memory writes, indirection reads, error unwinding, and local-scope management for Acid.

Key responsibilities:
- `error()` reports interpreter errors, unwinds IO stack, resets state, and longjmps to the main loop.
- `unwind()` pops local value frames from all symbols.
- `execrec()` roots the current command for GC and executes it.
- `execute()` handles statements, loops, conditionals, returns, local declarations, complex declarations, and expression statements.
- `bool()` converts Acid values to truth.
- `indir()` reads typed values from maps using format characters.
- `windir()` writes typed values back to core/symbol maps for `*=` and `@=`.
- `call()` binds actual/formal arguments, supports by-code formal parameters, sets return context, executes function body, and restores locals.

Important behavior:
- Expression statements are auto-printed via the default `print` call unless they are empty list results.
- `ret` is a global return context and function returns are implemented with `longjmp`.
- `indir()` supports integer widths, strings, runes, disassembly, and floating formats.
- Writes to non-core maps require write mode except for `cormap`.

Dependencies:
- Uses mach map accessors, evaluator, list/value structs, parser ASTs, and global error jmp state.

Notable risks:
- Longjmp-based control flow requires every temporary global state change to be restored on error paths.
- `windir()` allows writing to debuggee memory when enabled; format/size correctness matters.
