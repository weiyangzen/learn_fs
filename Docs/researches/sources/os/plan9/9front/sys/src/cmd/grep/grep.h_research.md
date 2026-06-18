# File Research: sources/os/plan9/9front/sys/src/cmd/grep/grep.h

Shared declarations for `grep`. It defines regex node types (`Re`), fragment pairs (`Re2`), DFA states, flags, buffers, global parser/search state, and prototypes.

The input buffer union reserves large `pre` and `buf` regions so long matching lines spanning reads can still be emitted as a suffix with preserved context. Flags cover count, filename, ignore-case, list-match/list-nonmatch, line numbers, status-only, invert, and unbuffered modes.
