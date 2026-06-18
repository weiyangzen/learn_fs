# File Research: sources/os/bsd/netbsd-src/lib/libcompat/regexp/regexp.c

Read completely: 1330 lines.

Implements Henry Spencer’s legacy regular-expression compiler and executor for NetBSD libcompat, exported with compatibility names such as `__compat_regcomp()` and `__compat_regexec()`. The compiler emits a compact bytecode program where each node is an opcode plus a two-byte relative next pointer, with operands stored inline for literals and character classes.

The parser supports anchors, `.`, bracket classes and ranges, grouping, alternation via `|` or newline, `*`, `+`, `?`, escaped literals, and BSD word-boundary escapes `\<` and `\>`. It compiles twice: first to count and validate bytecode size, then to allocate and emit the final `regexp` object. It also extracts optimization hints: required start character, anchoring, and a longest required literal for expensive patterns.

Execution uses global static match state, so calls are not reentrant. Matching is recursive for branches and subexpressions, with iterative handling for simple node chains and greedy `STAR`/`PLUS` through `regrepeat()`. Capturing groups fill the `startp`/`endp` arrays in the compiled object. Risks are mostly historical: global state, recursion/backtracking cost, fixed bytecode-size limit, byte-oriented character handling, and permissive old syntax rather than POSIX regex semantics.
