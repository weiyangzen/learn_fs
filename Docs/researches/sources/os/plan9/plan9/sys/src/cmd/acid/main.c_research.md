# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/main.c

Acid debugger program entry point, module loading, target attachment, GC, and utility allocation.

Key responsibilities:
- Parses options for kernel mode, write mode, library modules, machine type, quiet mode, and remote mode.
- Selects target executable or process text file, including `/proc/<pid>/text` and kernel system image lookup.
- Initializes formatters, Bio output, lexer keywords, variables, builtins, target maps, default modules, user modules, and symbol/register variables.
- Runs the interactive parse/evaluate loop with error recovery.
- Attaches executable and process files through libmach and process helpers.
- Loads machine-specific Acid modules from `/sys/lib/acid`.
- Loads user startup Acid files from `$home/lib/acid`.
- Allocates AST nodes, list nodes, constants, and GC-managed memory.
- Implements custom mark/sweep GC over nodes, lists, symbols, and strings.
- Handles notes, qid checks for process text changes, system-image lookup, numeric argument detection, and hex formatting.

Dependencies:
- Uses Plan 9 libmach, Bio, yacc parser, lexer, builtins, process-control helpers, and the Acid runtime structures.

Notable risks:
- The interpreter relies on global mutable state and nonlocal error unwinding.
- GC correctness depends on every live node/list/string being marked from symbols and current execution roots.
