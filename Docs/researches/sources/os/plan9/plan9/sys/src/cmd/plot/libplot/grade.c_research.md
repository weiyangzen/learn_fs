# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/grade.c

Sets curve subdivision grade.

Key responsibilities:
- Stores the supplied value in `e1->grade`.

Dependencies:
- Used by curve approximators such as `parabola()`.

Notable risks:
- No validation; zero or negative grade can break subdivision math.
