# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcolor1.c

Implements Level 1 extended color transfer operators.

Key behavior:
- `currentblackgeneration`, `currentcolortransfer`, and `currentundercolorremoval` return interpreter-stored procedure refs.
- `setblackgeneration` installs a black-generation procedure, asks the graphics state to use mapped transfer, and samples the procedure with `zcolor_remap_one`.
- `setcolortransfer` installs red/green/blue/gray transfer procedures and samples all four maps before resetting effective transfer.
- `setundercolorremoval` installs UCR and samples it with signed output support.

Dependencies and coupling:
- Reuses `zcolor_remap_one`, `zcolor_remap_color`, and `zcolor_reset_transfer` from `zcolor.c`.
- Uses estack continuations because transfer procedures are arbitrary PostScript procedures sampled into fixed-size maps.
