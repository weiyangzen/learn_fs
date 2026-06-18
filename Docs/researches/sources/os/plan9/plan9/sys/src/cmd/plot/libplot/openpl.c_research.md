# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/openpl.c

Initializes a plot session.

Key responsibilities:
- Calls backend initialization.
- Seeds base environment `e0` from the computed map rectangle.
- Copies `e0` into active environment `e1`.
- Moves current plot position to `(0, 0)`.

Important behavior:
- `sidey` and `scaley` are negative because screen y increases downward.
