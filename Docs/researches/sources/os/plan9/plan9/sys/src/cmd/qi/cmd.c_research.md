# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/cmd.c

Interactive debugger command parser and formatter for `qi`.

Key responsibilities:
- Parses simple expressions from symbols, dot, numeric constants, and one binary operator.
- Builds argument vectors for restart commands.
- Handles colon commands for break/delete/run/continue/step.
- Handles dollar commands for stack traces, breakpoint list, registers, floating registers, quit, trace toggles, and summaries/profiles.
- Formats memory/register values in multiple numeric, character, string, symbol, instruction, and source-line formats.
- Implements examine commands, expression evaluation, register assignment, command repetition, and interrupt handling.

Dependencies:
- Uses `run`, `reset`, `initstk`, breakpoint functions, memory accessors, libmach symbol/disassembly helpers, and `power.h` globals.

Notable risks:
- Expression parsing is intentionally small and not a full adb expression evaluator.
- String formats read until NUL without an explicit maximum local-buffer bound.
- Debugger control flow uses `setjmp/longjmp` shared with emulator faults.
