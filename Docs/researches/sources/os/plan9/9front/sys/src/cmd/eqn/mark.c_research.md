# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/mark.c

This file implements eqn `mark` and `lineup`.

Key responsibilities:
- `mark` stores the current horizontal position in troff register `09` with `\k(09`, marks the equation line as containing a mark, and leaves the input box as the result.
- `lineup` marks lineup usage and, when used standalone, creates a box that horizontally moves to the saved mark position.

Important implementation notes:
- `markline` is set to `1` for mark and `2` for lineup, letting `main.c` emit `.nr MK`.
- `lineup(1)` is used when a `LINEUP` precedes a box; `lineup(0)` creates an explicit alignment box.
