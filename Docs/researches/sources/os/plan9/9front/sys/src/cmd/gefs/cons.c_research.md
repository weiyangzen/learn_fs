# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/cons.c

Interactive gefs administrative console served through the `.cmd` service.

Key responsibilities:
- Parses console commands and dispatches to sync, halt, snapshot, check, user reload, config, space, and debug handlers.
- Sends administrative work to `fs->admchan` as `Amsg` requests for serialized background execution.
- Provides diagnostic dumps for fids, trees, users, block cache state, free ranges, and recent trace entries.
- Wraps commands that inspect trees in epoch protection.

Important behavior:
- `snap` supports list, delete, mutable fork, and label operations.
- `set`/`clear` can target either global config or a named snapshot.
- `show df` aggregates arena sizes and used/free space.
- `runcons()` tokenizes up to four fields, prints `gefs# ` prompts, and reports command errors through the gefs error stack.

Notable risks:
- `reserve` toggles `usereserve`, but its status print uses `permissive`, so its displayed transition is misleading.
- Command parsing is intentionally small and fixed-size; arguments with spaces are not supported.
