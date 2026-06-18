# File Research: sources/windows/reactos/drivers/filesystems/mup/dfs.h

This header declares the DFS stub interface consumed by MUP.

It defines context marker constants such as `DFS_OPEN_CONTEXT`, `DFS_DOWNLEVEL_OPEN_CONTEXT`, `DFS_CSCAGENT_NAME_CONTEXT`, and `DFS_USER_NAME_CONTEXT`, plus `DFS_NAME_CONTEXT` containing a UNC filename, context type, and flags.

It declares DFS pass-through, filesystem-control, create, cleanup, close, unload, and driver-entry routines.

Research notes:
- The constants are used by `mup.c`, especially `DFS_DOWNLEVEL_OPEN_CONTEXT`, to decide whether to bypass DFS logic and perform regular provider resolution.
- The declared API is broader than the stubbed implementation in `dfs.c`.
