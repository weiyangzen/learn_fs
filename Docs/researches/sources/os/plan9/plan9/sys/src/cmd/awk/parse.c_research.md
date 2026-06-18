# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/parse.c

AST construction and function-definition support for awk.

Provides:

- `nodealloc`, `node1` through `node4`.
- Statement constructors `stat1` through `stat4`.
- Expression constructors `op1` through `op4`.
- `celltonode()` and `rectonode()` for value nodes.
- `makearr()` to convert variables into awk arrays.
- `pa2stat()` for `pattern,pattern` range actions.
- `linkum()` for statement-list chaining.
- `defn()` for marking a symbol as a user function and storing its body.
- `isarg()` for function argument lookup.

It also contains pointer/integer conversion helpers used to store small integers in `Node *` slots.
