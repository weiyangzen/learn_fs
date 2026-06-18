# File Research: sources/os/plan9/9front/sys/src/cmd/rc/tree.c

Parse tree allocator and mutator. Uses a free-list of tree nodes and a per-parse `treenodes` list cleared by `freenodes()`.

Provides constructors, child attachment helpers, redirection epilogue attachment, simple-command normalization, function string generation, glob propagation, and token creation.

`simplemung()` wraps argument trees in `SIMPLE`, saves a printable function body string, and pulls redirections up to the command root.
