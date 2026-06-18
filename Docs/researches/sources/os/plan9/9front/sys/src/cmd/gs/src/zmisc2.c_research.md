# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zmisc2.c

## Purpose
Implements language-level query/change operators and the internal dictionary swapping needed to move between PostScript levels.

## Key Functions
- `zlanguagelevel()` returns current language level.
- `zsetlanguagelevel()` validates and switches language level.
- `set_language_level()` coordinates transitions among levels 1, 2, and 3.
- `swap_level_dict()` swaps level-specific dictionaries with systemdict entries.
- `swap_entry()` exchanges individual dictionary entries.

## Important Behavior
- Level-setting operators are available even in Level 1 mode.
- Level 1 hides globaldict by replacing its dictionary-stack slot with systemdict.
- Entering Level 2 enables dictionary auto-expansion; returning to Level 1 disables it.
- Level 3 availability depends on `ll3dict` being present.
- Name caches for globaldict entries are invalidated when dropping to Level 1.

## Research Notes
Interpreter mode-management code with careful VM-space bypasses for system dictionaries.
