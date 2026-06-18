# File Research: sources/os/plan9/9front/sys/src/cmd/rc/exec.h

Interpreter interface header for `rc`. Declares opcode entry points, stack/value helpers, redirection types, thread state, builtin dispatch, and status helpers.

Defines `word`, `list`, `redir`, and `thread`, including code pointer, pc, argv stack, redirection stack, local variables, lexer, child pid, saved status, and return frame.

The header is the shared contract between compiler/parser output and runtime execution, especially the `X*` opcode functions used in generated `code` vectors.
