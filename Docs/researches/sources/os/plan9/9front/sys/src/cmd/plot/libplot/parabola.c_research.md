# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/parabola.c

`parabola.c` approximates a quadratic curve through two endpoints and a bend/control point. It chooses step sizes from endpoint distances, the environment quantum, and grade, then emits line segments via `vec()`.
