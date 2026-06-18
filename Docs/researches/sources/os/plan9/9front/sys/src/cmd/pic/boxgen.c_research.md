# File Research: sources/os/plan9/9front/sys/src/cmd/pic/boxgen.c

## Role

Generates `pic` box objects.

## Main Behavior

`boxgen` reads default box height/width, applies attributes for size, `same`, `with` corner/edge anchoring, `at`, invisibility, no edge, dotted/dashed outline, fill, and text.

If no explicit position is provided, the box is placed relative to the current point and current direction. `with` adjusts the anchor so a named side/corner lands at the current point.

The object stores width, height, drawing attributes, dash/dot value, and fill value. Bounds are added via `extreme`, and current position is advanced to the far edge in the active direction.

## State

Previous box height/width are remembered for the `same` attribute.
