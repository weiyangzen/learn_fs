# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/for.c

This file implements `grap` loop and conditional expansion. A fixed stack of `For` records stores loop variable, limit, operator, step, and body text.

`forloop` initializes the variable and pushes the loop body back onto the input stream. `endfor` advances the variable by `+`, `-`, `*`, or `/`, then schedules the next iteration through `nextfor`.

`ifstat` chooses then/else body text, pushes the chosen source back for parsing, and frees the unused branch.

Notable limitation: `nextfor` has a `BUG` comment that termination should depend on operator and direction; currently it checks `var > SLOP * to`.
