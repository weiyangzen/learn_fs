# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/startup.c

This RISC OS helper enforces a single running Antiword application instance.

Key behavior:
- Enumerates running tasks through `TaskManager_EnumerateTasks`.
- Performs case-insensitive task-name comparison.
- If Antiword is not running, chains `<Antiword$Dir>.!Antiword`, optionally passing a filename.
- If Antiword is running and a filename is supplied, sends a `message_DATALOAD` as if the file was dropped on the iconbar icon.
- If Antiword is already running without a file argument, reports an error.

Important details:
- Checks the filename length against the Wimp dataload message buffer.
- Debug builds append redirection to `<Antiword$Dir>.Debug`.

Filesystem relevance:
- Directly passes user-selected document paths to the running app and launches the application from the RISC OS application directory.
