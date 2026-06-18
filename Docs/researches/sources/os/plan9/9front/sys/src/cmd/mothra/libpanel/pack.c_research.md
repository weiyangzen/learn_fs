# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/pack.c

Implements libpanel layout calculation.

Key behavior:
- Recursively computes children’s requested sizes, applies `MAXX/MAXY`, and derives each panel’s `sizereq`.
- Honors fixed-size, fill, expand, pad, ipad, pack side, and placement flags.
- Distributes slack among `EXPAND` children along the relevant axis.
- Assigns rectangles recursively and computes child spaces through widget callbacks.
- `plmove()` translates an already-packed panel tree and calls `plemove()` for edit panels.

Important dependencies: widget `getsize`/`childspace` methods, panel flags.

Notable risks:
- Layout mutates `sizereq` during slack distribution.
- `plmove()` special-cases edit widgets because text locations are absolute.
