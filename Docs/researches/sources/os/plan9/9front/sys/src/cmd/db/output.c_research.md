# File Research: sources/os/plan9/9front/sys/src/cmd/db/output.c

Purpose: Output buffering, column tracking, and debugger input/output redirection.

Key behavior:
- `outputinit()` initializes buffered stdout and installs `%t` tab formatting.
- `dprint()` formats to a local buffer, writes through `Biobuf`, and tracks display column by runes/newlines.
- `flushbuf()`, `flush()`, `printc()`, `prints()`, and `newline()` wrap output operations.
- `iclose()` manages nested input redirection stack for `$<`/`$<<`.
- `redirout()` appends to or creates output redirection targets.
- `oclose()` restores stdout output buffering.
- `endline()` emits a newline when the current column exceeds `maxpos`.

Notable details:
- `%t` no longer does calculated tab stops; it prints a literal tab.
- On `mkfault`, `dprint()` suppresses output.
