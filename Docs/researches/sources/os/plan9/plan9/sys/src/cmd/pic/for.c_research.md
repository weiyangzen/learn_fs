# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/for.c

Implements `pic` `for` loops and `if` source expansion. Loop state is stored on a fixed stack of ten `For` frames.

`forloop` installs the loop variable, stores limit/operator/increment/body, and pushes the first iteration body back into the input stream. `endfor` updates the variable using `+`, `-`, `*`, or `/`, then schedules the next iteration.

The loop completion test is simple and noted as direction-insensitive: it stops when the variable exceeds `to * 1.001`.

`ifstat` pushes either the then-body or else-body back into input and frees the unused body.
