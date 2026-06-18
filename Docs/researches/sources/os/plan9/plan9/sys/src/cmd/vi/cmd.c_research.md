# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/cmd.c

Purpose: Interactive command interpreter for the MIPS simulator.

Key behavior:
- Parses adb-like commands for running, continuing, stepping, resetting, setting breakpoints, dumping registers, stack traces, instruction/stat summaries, expression evaluation, memory display, and register assignment.
- Supports symbolic and numeric expressions using `+`, `-`, `%`, `&`, and `|`.
- `pfmt` implements memory/value formats for octal, decimal, hex, bytes, chars, strings, symbols, instructions, source lines, and globals.
- Handles repeat counts and repeats the last command on blank input.
- Installs an interrupt note handler that stops the run loop.

Dependencies:
- Uses Plan 9 `Biobuf`, `mach` symbols, memory accessors, run loop, breakpoints, stats, and source/symbol helpers.

Notable details:
- This `vi` is a simulator/debugger command shell, not the visual editor.
