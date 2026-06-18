# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/size.c

This file manages local and global point-size changes.

Key responsibilities:
- `setsize` parses relative and absolute size strings and pushes size-stack state.
- `size` wraps a box with troff size changes and restores the previous size.
- `globsize` changes the global size and recomputes default sub/sup delta unless explicitly set.

Important implementation notes:
- Absolute local sizes save the current troff size in numbered registers.
- `DPS` is used for relative transitions; `ABSPS` is used for absolute transitions.
- Invalid size strings generate warnings and leave state mostly unchanged.
