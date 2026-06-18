# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/glob.c

This file defines eqn’s global state and default device configuration.

Key contents:
- Default typesetter is `"post"` and device type is `DEVPOST`.
- Default minimum size is 4.
- Debug flag, parser box stack `lp`, string-register usage table, current point size, global size, font, font stack, size stack, display mode, and syntax-error flag.
- Box metadata arrays: `eht`, `ebase`, `lfont`, `rfont`, `lclass`, `rclass`.
- Final equation state: `eqnreg`, `eqnht`.
- Inline delimiter chars and mark/lineup state.

Important implementation notes:
- This file is pure shared state; most eqn files read and mutate these globals.
- The default font is initialized to italic position `'2'`.
