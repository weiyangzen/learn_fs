# File Research: sources/os/plan9/9front/sys/src/cmd/pic/linegen.c

## Role

Generates `pic` line, arrow, and spline objects.

## Main Behavior

`linegen` processes attributes for text, arrow heads, invisibility, no edge, dotted/dashed style, `same`, direction/length, `to`, `by`, `then`, `from`/`at`, `with`, `chop`, and fill.

It accumulates one or more segment deltas in `dx[]`/`dy[]`. Direction attributes add default or explicit lengths. `to` and `by` start new segments when needed. If no movement is specified, it emits a default movement in the current direction.

## Chopping And Arrows

`chop` shortens the first and last segment by configured distances, defaulting to circle radius when only bare `chop` is used. Arrow objects default to a head at the endpoint, and explicit head attributes are honored.

## Output

The object stores final endpoint, arrow dimensions, number of segment deltas, per-segment deltas, attributes, dash/dot value, and fill value. It updates global extrema for straight lines/arrows and approximate spline extrema.

## State

Last line delta is remembered for the `same` attribute, and current position/direction are updated as attributes are processed.
