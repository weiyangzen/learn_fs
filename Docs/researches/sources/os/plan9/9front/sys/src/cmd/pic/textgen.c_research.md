# File Research: sources/os/plan9/9front/sys/src/cmd/pic/textgen.c

`textgen.c` creates `TEXT` and `TROFF` objects. `textgen()` consumes height, width, `with`, `at`, `invis`, and text attributes, saves strings in the global `text` array, computes a text bounding box, updates extrema, creates the object, and advances `curx/cury` according to current direction.

`troffgen()` stores raw troff commands via the same text storage mechanism and creates a `TROFF` node. `savetext()` grows the text array and records text type and string pointer.
