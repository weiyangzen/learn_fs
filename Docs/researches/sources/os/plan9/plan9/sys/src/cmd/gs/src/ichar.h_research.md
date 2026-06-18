# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ichar.h

Defines execution-stack layout and helpers for character rendering operators. The `snumpush` frame stores the text enumerator, procedure slots, saved stack depths, saved gstate level, saved font/root font, completion proc, and mark.

Exports support functions from `zchar.c`, including show setup/continuation/free, glyph refs, stringwidth finish, cachedevice operators, and width-only inspection.
