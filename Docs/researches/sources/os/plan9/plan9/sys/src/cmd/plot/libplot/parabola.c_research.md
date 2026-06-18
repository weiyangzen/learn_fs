# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/parabola.c

Approximates a quadratic curve using line segments.

Key responsibilities:
- Takes start, end, and bend/control point coordinates.
- Computes quadratic coefficients.
- Subdivides based on distances to the control point, `e1->quantum`, and `e1->grade`.
- Emits vectors from start to end through sampled points.

Important behavior:
- Falls back to a straight line when either endpoint is within `quantum` of the control point.

Notable risks:
- `e1->grade` is used as a divisor without validation.
