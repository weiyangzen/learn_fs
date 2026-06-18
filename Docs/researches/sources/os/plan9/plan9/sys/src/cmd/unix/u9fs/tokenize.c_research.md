# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/tokenize.c

- Role: Tokenizes mutable strings using Plan 9 UTF-aware delimiter scanning.
- Key functions: `getfields` splits on any rune in `set`; `tokenize` splits on whitespace.
- Integration: Declared in `plan9.h`; used by control-message parsing and argument handling patterns.
- Risks/notes: Modifies the input buffer in place by writing NULs.
