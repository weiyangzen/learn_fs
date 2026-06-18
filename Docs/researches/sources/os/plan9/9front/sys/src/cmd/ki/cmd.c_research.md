# File Research: sources/os/plan9/9front/sys/src/cmd/ki/cmd.c

Interactive command interpreter for `ki`. It parses simple address expressions, repeats the last command on blank input, supports breakpoint/run/continue/step commands via `:`, debugger summaries and register dumps via `$`, memory examination via `/` and `?`, expression evaluation via `=`, and register assignment via `>`.

`pfmt` implements output formats for octal/decimal/hex integers, bytes, characters, strings, symbols, globals, disassembly, source locations, and line breaks. `colon` integrates with execution control and reports stopped/breakpoint locations. `catcher` maps interrupts into debugger stops. This file is the user interface over the simulator core.
