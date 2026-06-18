# File Research: sources/os/plan9/9front/sys/src/cmd/rc/code.c

This file compiles `rc` parse trees into the shell’s internal bytecode representation.

Key responsibilities:
- Maintains `codebuf`, `codep`, `ncode`, and source line tracking.
- `compile()` initializes bytecode, stores reference count and source file name, compiles a tree, and appends `Xreturn`.
- `morecode()` grows the bytecode buffer.
- `stuffdot()` patches forward jump addresses.
- `noglobs()` removes glob markers where a literal string or pattern is expected.
- `outcode()` recursively emits bytecode for all major shell syntax nodes: variables, quoting, substitution, background jobs, sequencing, concatenation, command substitution, conditionals, functions, loops, words, redirections, assignments, pipes, subshells, switches, matches, and simple commands.
- `codeswitch()` emits the switch/case bytecode layout with jump patching and final `Xpopm`.
- `iscase()` recognizes literal `case` commands in switch bodies.
- `codecopy()` and `codefree()` implement reference-counted bytecode lifetime, freeing owned strings according to opcode layout.

Implementation notes:
- `outcode()` emits `Xsrcline` records when source line changes.
- Background jobs synthesize `/dev/null` read redirection and optionally emit a Plan 9 `rfork s` builtin call.
- Some tree strings transfer ownership into bytecode by setting `t->str = 0`.
