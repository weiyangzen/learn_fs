# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/spline.c

Uniform quadratic spline renderer.

Key responsibilities:
- Iterates point-list groups from `num[]` and `ff[]`.
- Handles open and closed spline modes.
- Converts adjacent guide points into midpoint-to-midpoint parabolic spans.
- Uses `parabola()` and occasional `plotline()` to render the result.

Important behavior:
- `mode == 4` draws a closed curve.
- Odd modes draw a doubled first endpoint.
- Modes `>= 2` except closed mode draw the final endpoint segment.

Notable risks:
- For `n < 3`, it draws a line using the first two points; malformed counts under 2 would read past input.
