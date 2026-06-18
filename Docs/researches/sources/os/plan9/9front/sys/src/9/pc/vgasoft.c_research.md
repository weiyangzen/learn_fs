# File Research: sources/os/plan9/9front/sys/src/9/pc/vgasoft.c

## Role

Software cursor fallback for the Plan 9 VGA layer.

## Main Interfaces

- Exports `VGAcur vgasoftcur` named `soft`.
- Main routines: `swenable`, `swdisable`, `swload`, and `swmove`.

## Key Behavior

- `swenable()` marks the screen as using a software cursor and loads the default cursor.
- `swdisable()` clears software cursor state.
- `swload()` copies cursor data into `scr->Cursor`.
- `swmove()` updates `scr->pos`.

## Dependencies And Assumptions

- Depends only on generic `VGAscr` cursor fields and the global default `cursor`.
- Actual drawing/erasing of the software cursor is handled elsewhere in the screen layer.

## Research Notes

- This tiny module provides a universal fallback when no chipset hardware cursor is selected.
