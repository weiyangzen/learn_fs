# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/grap.y

This yacc grammar defines the `grap` language parsed inside `.G1` blocks. It covers graph blocks, statements, frames, ticks, grids, labels, coordinates, plots, lines, circles, draw/next paths, copy/thru includes, for loops, if statements, assignments, strings, formatted strings, points, and numeric expressions.

The grammar actions call the module functions in `grap.h` to update state and emit `pic` output through the temp file. Expressions include arithmetic, comparisons, boolean operators, log/exp/trig/sqrt/random/min/max/int, variable lookup, and assignment.

Multi-line patterns such as `copy thru` and loop/conditional bodies are handled by pushing source strings back into the lexer/input stack.
