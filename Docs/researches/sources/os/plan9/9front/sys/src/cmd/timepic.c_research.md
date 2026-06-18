# File Research: sources/os/plan9/9front/sys/src/cmd/timepic.c

`timepic.c` converts `.TPS` timing-diagram blocks into pic `.PS/.PE` drawing commands while passing other input lines through.

Data model:
- `Symbol`: named numeric expression bindings.
- `Event`: timestamp, value type, optional data label, optional vertical marker line.
- `Signal`: signal name and event list.

Parsing:
- `lex()` tokenizes commands, symbols, numbers, strings, punctuation, and EOF.
- `expr()`, `term()`, and `factor()` implement arithmetic expressions.
- `assign()` binds numeric symbols.
- `events()` parses event timelines, relative `+` offsets, repeats with `{...}`, labels, and marker `|`.
- `signal()` parses one signal definition.

Rendering:
- `.TPS width rowheight` starts a diagram.
- `.TPE` ends it.
- `sigout()` renders each signal as high/low/z/unknown/multivalue waveforms.
- `slantfill()` draws diagonal fill for unknown (`x`) intervals.
- `diagram()` computes extents and emits pic output.

Integration:
- `main()` processes stdin or each file.
- Non-`.TPS` input is copied unchanged.

Risk notes:
- `cleansym()` frees `Event` nodes but not `Event.data`, unlike `freeev()`; this is a small leak per diagram.
- Error reporting is non-fatal; parser often continues after reporting syntax problems.
