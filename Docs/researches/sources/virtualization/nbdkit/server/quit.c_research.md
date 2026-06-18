# File Research: sources/virtualization/nbdkit/server/quit.c

This file implements process shutdown signaling. It defines global volatile `quit` and a wakeup object used by polling loops: a pipe on POSIX and an Event on Windows.

On POSIX, `set_up_quit_pipe` creates a close-on-exec pipe, `close_quit_pipe` closes both ends, and `set_quit` is intentionally async-signal-safe: it sets `quit = 1` and writes one byte to the pipe. Comments explicitly warn against unsafe work in signal handlers, citing signal-safety concerns.

On Windows, the same abstraction is implemented with `CreateEvent`, `SetEvent`, and `CloseHandle`. `handle_quit` is the signal-handler entry point, and public `nbdkit_shutdown` triggers the same quit path for plugin/filter initiated server shutdown.
