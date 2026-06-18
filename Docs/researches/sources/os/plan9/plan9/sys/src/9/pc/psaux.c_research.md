# File Research: sources/os/plan9/plan9/sys/src/9/pc/psaux.c

Raw PS/2 auxiliary port arch-file interface for user-level mouse handling.

Key elements:
- Maintains global queue `psauxq`.
- `psauxputc` enqueues raw aux bytes from i8042 callback.
- `psauxread` reads bytes from the queue.
- `psauxwrite` sends command bytes to the aux device via `i8042auxcmds`.
- `psauxlink` opens a nonblocking queue, enables aux callback, and registers architecture file `psaux` with exclusive `0660` permissions.

Interactions:
- Shares draw/cursor includes with mouse/screen code but bypasses decoded kernel mouse handling.
- Uses i8042 aux support.

Research notes:
- Explicit BUG note: shift state is ignored.
- Provides raw input path for user-space daemons.
