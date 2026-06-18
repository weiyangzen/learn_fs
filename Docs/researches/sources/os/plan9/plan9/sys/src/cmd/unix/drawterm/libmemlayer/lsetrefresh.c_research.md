# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/lsetrefresh.c

Switches a layer between refresh-function and backing-store modes.

Key function:
- `memlsetrefresh`: updates an existing refresh function, drops save backing when switching to refresh mode, or allocates save backing and populates it when switching to backup mode.

Important behavior:
- When moving from refresh to save-backed mode, calls the old refresh function over the full layer rectangle to initialize the new save image.
