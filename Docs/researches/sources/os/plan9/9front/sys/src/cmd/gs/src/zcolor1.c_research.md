# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcolor1.c

This file implements Level 1 extended color operators for transfer, black generation, and undercolor removal.

Key behavior:
- Provides current-state operators:
  - `currentblackgeneration`
  - `currentcolortransfer`
  - `currentundercolorremoval`
- `setblackgeneration` installs a PostScript black-generation procedure and samples it into the graphics transfer map.
- `setcolortransfer` installs red, green, blue, and gray transfer procedures and remaps all four.
- `setundercolorremoval` installs an undercolor-removal procedure and samples it with signed output support.
- Invalidates current device color after remapping so later painting uses updated transfer behavior.

Important dependencies:
- Reuses shared remapping helpers from `zcolor.c`.
- Calls graphics-library remap setters from `gscolor1.h`.

Research notes:
- The main complexity is sequencing e-stack remap continuations for one or four procedure maps.
