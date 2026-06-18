# File Research: sources/teaching/xv6-public/sh.c

Minimal xv6 shell.

Key behavior:
- Supports command execution, redirection, pipelines, command lists with `;`, background execution with `&`, and parenthesized blocks.
- Built-in `cd` runs in the parent shell process.
- Ensures fds 0, 1, and 2 are open to `console`.
- Parses input into command structs: exec, redir, pipe, list, and back.
- `runcmd` recursively executes the parsed command tree using `fork`, `exec`, `pipe`, `dup`, `open`, `close`, and `wait`.
- Tokenizer recognizes whitespace and shell symbols `<|>&;()`, with `>>` parsed but implemented with create/write-only semantics rather than append.
- `nulterminate` mutates the input buffer to terminate parsed argv/file strings.

Limitations:
- No quoting, globbing, variables, append offset semantics, or job control.
