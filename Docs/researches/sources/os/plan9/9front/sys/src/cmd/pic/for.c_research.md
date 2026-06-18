# File Research: sources/os/plan9/9front/sys/src/cmd/pic/for.c

## Role

Implements `pic` loop and conditional source expansion.

## For Loops

`forloop` pushes a loop frame with variable name, limit, operator, step, and saved source string. It initializes the variable and calls `nextfor`.

`nextfor` checks loop completion using a small slop factor and either frees/pops the frame or pushes the saved body plus an `Endfor` marker back onto the input stack.

`endfor` updates the loop variable by add, subtract, multiply, or divide, then continues through `nextfor`.

## Conditionals

`ifstat` pushes either the then-part or else-part source text back onto the input stream and frees the unused branch. It returns the branch string that will be freed later by the input stack.
