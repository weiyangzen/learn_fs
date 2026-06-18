# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/paren.c

This file builds scalable delimiters around an equation box for `left ... right ...`.

Key responsibilities:
- Computes delimiter height from the inside box height.
- Handles special cases for braces, floors, ceilings, brackets, parentheses, vertical bars, and custom delimiters.
- Builds tall delimiters from top/middle/bottom glyph pieces with `brack`.
- Centers or shifts the inside box based on baseline balance.
- Updates height and baseline for the parenthesized result.

Important implementation notes:
- PostScript output applies a small delimiter vertical shift through `Parenshift`.
- Brace height is forced odd and at least three parts.
- `left n`/empty left delimiter emits no left delimiter.
