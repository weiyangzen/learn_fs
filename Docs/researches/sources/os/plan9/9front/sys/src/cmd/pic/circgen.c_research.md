# File Research: sources/os/plan9/9front/sys/src/cmd/pic/circgen.c

## Role

Generates `pic` circle and ellipse objects.

## Main Behavior

`circgen` handles both `CIRCLE` and `ELLIPSE`. It reads default radii from global variables, applies attributes for text, radius, diameter, width, height, `same`, `with`, `at`, invisibility, no edge, dotted/dashed outline, and fill.

For circles, the vertical radius is forced to equal the horizontal radius. For ellipses, width and height map to separate radii.

If no explicit `at` is provided, placement advances from the current point in the current direction by the relevant radius. `with` anchors sides/corners using full radius offsets or approximate diagonal offsets.

## Output

The generated object stores radii, attributes, dash/dot value, and fill value. It updates global extrema and advances current position by radius in the active direction.

## State

Previous circle and ellipse radii are remembered separately for the `same` attribute.
