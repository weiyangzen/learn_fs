# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smboptable.c

Defines SMB and transaction2 dispatch tables.

Key data:
- `smboptable[256]` maps SMB command opcodes to names, process functions, and debug flags.
- `smbtrans2optable[]` maps transaction2 opcodes to names/process functions.
- `smbtrans2optablesize` exposes transaction2 table length.

Implemented command mappings include:
- Directory create/delete/check, open/create/close/flush/delete/rename, query/set info, write, locking AndX, transaction, echo, open/read/write AndX, transaction2, find close2, tree disconnect/connect AndX, negotiate, session setup AndX, and NT create AndX.

Notable details:
- Many legacy/raw/print/search/NT transaction commands are named but unimplemented with nil process pointers.
