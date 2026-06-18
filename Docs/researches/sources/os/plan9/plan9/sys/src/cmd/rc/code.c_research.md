# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/code.c

Compiler from rc parse trees to the shell’s bytecode-like `code` vector.

Main components:
- `morecode()` grows compiler output.
- `compile()` initializes code, emits tree code, reads heredocs, appends `Xreturn`, and returns success/failure.
- `outcode()` recursively emits `X*` opcodes for rc syntax: variable expansion, quoted expansion, subscripts, async, sequencing, concatenation, backquote, conditionals, loops, functions, switch, redirection, assignment, pipes, pipefd, globbing, and simple commands.
- `codeswitch()` emits the switch/case control-flow skeleton using patched jumps.
- `iscase()` recognizes `case` commands in switch bodies.
- `fnstr()` converts a tree back to command text for function definitions and no-fork fallback paths.
- `codecopy()`/`codefree()` manage reference counts and free embedded strings/function text.

Risk/notes:
- In no-fork builds, async/backquote/subshell/pipe snippets are stored as strings to run through a new rc.
- Jump patching uses `stuffdot()` with placeholder code slots.
- `if not` correctness uses `runq->iflast` static checking.
