# File Research: sources/os/plan9/9front/sys/src/cmd/grap/for.c

Implements `for` loops and `if` statement expansion for `grap`. A fixed stack stores loop variable, limit, operator, increment, and body string. `forloop` initializes the variable and pushes the body back into input; `endfor` updates by `+`, `-`, `*`, or `/`.

`ifstat` chooses then/else text based on numeric truth, pushes the selected text into the input stream, and frees unused text. Loop termination is noted as direction/op-limited by an in-source BUG comment.
