# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcontrol.c

Implements Ghostscript/PostScript control-flow and execution-stack operators.

Key behavior:
- Defines `exec`, `.execn`, `superexec`, `.runandhide`, `if`, `ifelse`, `for`, `%for_samples`, `repeat`, `loop`, `exit`, `stop`, `.stop`, `stopped`, `.stopped`, `currentfile`, `execstack`, and `countexecstack`.
- Uses continuation operators on the execution stack for looping, conditionals, stopped contexts, CIE sample loops, and `cond`.
- `pop_estack` unwinds execution frames and runs cleanup procedures attached to execution-stack marks.
- `count_to_stopped` locates matching stopped frames by signal mask; unmatched `exit`/`stop` synthesizes a quit with `invalidexit`.
- `execstack` copies the execution stack into a user array while sanitizing internal operators and transient structs.

Dependencies:
- Heavily tied to `estack`, `oper`, `files`, packed arrays, operand/ref stacks, and interpreter file-cache handling.

Research notes:
- This file is core interpreter control machinery. Correct stack-depth accounting, hidden execution marks, and cleanup execution are the main risk areas.
