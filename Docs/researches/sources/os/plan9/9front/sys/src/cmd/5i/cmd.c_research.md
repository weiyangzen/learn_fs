# File Research: sources/os/plan9/9front/sys/src/cmd/5i/cmd.c

This file implements the interactive command shell, expression parser, formatting, run/step commands, register setting, tracing toggles, and memory/source inspection for `5i`.

Parsing and expressions:
- `nextc()` skips spaces/tabs and terminates newline.
- `numsym()` parses a symbol, `.`, `#hex`, or numeric constant.
- `expr()` evaluates one binary operation over symbols/numbers: `+`, `-`, `%` as division, `&`, or `|`.
- `buildargv()` tokenizes command strings for restart arguments.

Command groups:
- `colon()` handles:
  - `:b` set breakpoint,
  - `:d` delete breakpoint,
  - `:r` reset/restart with args and run,
  - `:c` continue,
  - `:s` step optional count.
  It reports stopped or breakpoint address and optionally source.
- `dollar()` handles stack traces, breakpoint list, register dumps, quit, summaries, trace mode toggles, and instruction/TLB/segment/profile summaries.
- `eval()` prints expression values.
- `quesie()` implements memory/executable inspection with format sequences.
- `setreg()` writes PC, SP, or `rN`.

Formatting:
- `pfmt()` supports octal/decimal/hex signed/unsigned 16/32-bit output, bytes/chars/escaped chars, strings, escaped strings, time, address symbolization, globals, disassembly, newline, direction modifiers, and source-line display.
- Updates global `dot`, `fmt`, and `inc` for repeated inspection.

Main shell:
- `cmd()` installs interrupt handler, initializes `dot`, recovers through `setjmp(errjmp)`, reads commands from `bin`, repeats last command on blank line, parses optional address/count, and dispatches by command character `$`, `:`, `/`, `?`, `=`, or `>`.

Dependencies and interactions:
- Uses `run()`, `reset()`, memory accessors, symbol lookup/disassembly, source printing, breakpoints, summaries, and register state.
- Driven after `5i.c` loads the executable.

Research relevance:
- User-facing debugger shell for `5i`.

Risk notes:
- Command parsing is simple and buffer-limited.
- `expr()` supports only one binary operator, not full expression precedence.
- Some output calls pass dynamic strings as format strings to `Bprint`, following Plan 9 conventions but requiring trusted symbol text.
