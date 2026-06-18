# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/bwatch.c

Optional debug lock-order watcher for fossil blocks.

It maintains a score-parent dependency map derived from block contents and per-thread lists of currently locked blocks. On each block lock, it detects attempts to lock an ancestor after holding a descendant, or an out-of-order sibling path, then stops the process via `/proc` control for debugging.

The file is explicitly described as very slow and unreliable once snapshots make the structure a DAG rather than a tree, but useful for catching lock-order bugs during development.
