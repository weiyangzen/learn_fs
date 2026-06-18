# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/boxgen.c

Generates rectangular `pic` box objects. It consumes attributes for height, width, same-as-previous sizing, with-corner anchoring, explicit `at`, invisibility, no-edge, dot/dash style, fill, and text.

If no explicit position is supplied, placement follows the current direction and advances by half the box dimension before creating the object. After creation it advances `curx/cury` to the exiting edge.

The object stores width, height, style bits, dash/dot value, and fill value, and updates drawing extremes to include the box bounds.
