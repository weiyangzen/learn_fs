# File Research: sources/os/plan9/9front/sys/src/cmd/pic/blockgen.c

## Role

Implements `pic` block handling for bracketed object groups and brace-local movement groups.

## Block Stack

`leftthing` saves current position, direction, bounds, and symbol context when entering `[...]`; it resets local coordinates and creates a `BLOCK` object. For `{...}`, it saves position/direction on a separate stack.

`rightthing` restores saved state. For `]`, it creates a `BLOCKEND`, links begin/end object indices, stores local bounding box information, and restores outer bounds. For `}`, it emits a `MOVE`.

## Block Generation

`blockgen` applies attributes such as height, width, `with`, explicit position, invisibility, and text. It computes final block placement, updates global extrema, stores size and original local center, advances current position, copies block metadata to the end marker, and calls `blockadj`.

`blockadj` shifts all enclosed objects by the block placement delta, including absolute coordinate fields for lines, splines, and arcs.

## Limits

Nested `[...]` and `{...}` depth is bounded by fixed stack sizes.
