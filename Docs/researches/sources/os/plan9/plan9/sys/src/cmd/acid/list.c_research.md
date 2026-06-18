# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/list.c

Acid list construction, mutation, comparison, and stack-trace list helpers.

Key responsibilities:
- Constructs runtime lists from AST list nodes.
- Computes list length and marks lists for GC.
- Concatenates lists, appends values, deletes elements, compares lists, and retrieves nth elements.
- Creates single-value lists from variables.
- Builds lists of local variables and parameters from libmach symbols and frame data.
- Builds a trace list for the current stack frame with locals and parameters.

Dependencies:
- Uses `List`, `Node`, `Map`, `Symbol`, `gmalloc`, `expr`, `listvar`, libmach symbol APIs, and stack/register state.

Notable risks:
- List mutation copies value fields manually.
- Stack trace local/parameter extraction is target-symbol dependent.
