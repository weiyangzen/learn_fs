# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/move.c

This file implements explicit movement commands: `fwd`, `back`, `up`, and `down`.

Key responsibilities:
- Converts the movement amount from hundredths of an em into current-size ems with `EM`.
- Rewrites the box string to include horizontal (`\h`) or vertical (`\v`) motion around the original box.
- Leaves height and baseline metadata unchanged.
- Returns the moved box as `yyval`.

Important implementation notes:
- Horizontal movement prefixes the box with positive or negative `\h`.
- Vertical movement wraps the box in equal and opposite vertical shifts so subsequent output resumes at the original baseline.
