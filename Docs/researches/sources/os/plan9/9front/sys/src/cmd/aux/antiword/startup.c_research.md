# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/startup.c

RISC OS launcher that enforces a single running Antiword task.

Key responsibilities:
- Enumerates running tasks and compares task names case-insensitively.
- Starts `!Antiword` if no existing Antiword task is active.
- If Antiword is already running and an argument is supplied, sends it as a simulated iconbar drag-and-drop `DATALOAD` message.
- Reports an error if Antiword is already running and no file argument is provided.

Dependencies:
- DeskLib event/error/SWI APIs, TaskManager enumeration, Wimp messaging, RISC OS filetype constants.

Research relevance:
- Small platform-specific process coordination wrapper.
