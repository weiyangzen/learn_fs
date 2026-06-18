# File Research: sources/os/plan9/plan9/sys/src/cmd/cb/cb.h

Shared definitions and global state for `cb`. It defines keyword/operator type constants, spacing flags, indentation limits, buffer sizes, output macros, and helper macros for eating whitespace.

It declares the `indent`, `keyw`, and `op` structures and initializes global keyword and operator tables directly in the header. It also defines formatter global variables including input/output buffers, indentation stack, do/if tracking, parser flags, lookahead buffers, width counters, and line state.

Function prototypes cover all formatter operations implemented in `cb.c`, including lexical handling, indentation output, comments, operators, lookahead, and EOF error reporting.
