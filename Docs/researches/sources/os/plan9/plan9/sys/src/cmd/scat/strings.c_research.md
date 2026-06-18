# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/strings.c

Defines static lookup tables used by `scat`.

Key contents:
- `greek[]` maps 1-based indexes to spelled Greek letter names.
- `greeklet[]` maps the same indexes to Unicode Greek `Rune` values.
- `constel[]` maps 1-based constellation indexes to three-letter abbreviations.
- `names[]` maps object-type command strings and abbreviations to `Type` values.

Behavior notes:
- This file is included directly by `scat.c`, not compiled as an independent module.
- The tables drive Bayer-name parsing, display-name formatting, and type-based lookup/culling.
