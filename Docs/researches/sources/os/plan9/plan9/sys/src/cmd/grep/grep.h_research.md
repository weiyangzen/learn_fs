# File Research: sources/os/plan9/plan9/sys/src/cmd/grep/grep.h

This is the shared header for the custom Plan 9 `grep`. It defines regex node (`Re`), regex fragment (`Re2`), DFA state (`State`), node types, limits, pseudo input symbols, command flags, global buffers, and global parser/search state.

The input buffer union provides both pattern-class string space and search buffers with `pre`/`buf` halves so very long matching lines retain a suffix across reads.

It declares regex construction, lexer/parser, state allocation, follow computation, search, and debug print functions.
