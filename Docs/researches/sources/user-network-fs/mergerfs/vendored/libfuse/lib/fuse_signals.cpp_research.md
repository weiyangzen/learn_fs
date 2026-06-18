# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_signals.cpp

## Purpose
`fuse_signals.cpp` installs and removes process signal handlers that request FUSE session shutdown.

## Important APIs, Types, and Functions
Public functions are `fuse_set_signal_handlers(struct fuse_session*)` and `fuse_remove_signal_handlers(struct fuse_session*)`. A static atomic `g_fuse_instance` points to the current session. `exit_handler` calls `fuse_session_exit`. `set_one_signal_handler` conditionally sets or restores handlers.

## Control Flow
Setup installs `exit_handler` for SIGINT, SIGTERM, and SIGQUIT, ignores SIGPIPE, then stores the session pointer. Removal restores default handlers for signals that still point to the installed handlers and clears the atomic if it matches the session.

## State and Persistence
Only the process-global atomic session pointer persists. Handlers affect process-wide signal disposition, not just the FUSE instance.

## Dependencies and Integration Points
This file depends on `fuse_lowlevel.h`, atomics, and POSIX `sigaction`. `helper.cpp` installs handlers after mount/daemonize and removes them during teardown. `fuse_loop.cpp` observes session exit.

## Risks
Signal disposition is process-global, so embedding this library in a process with its own handlers can conflict. The conditional restore logic only resets handlers if they match expected values; external handler changes may remain. The handler only toggles an atomic/session flag, which is appropriate for async-signal safety.

## Test Signals
Test SIGINT/SIGTERM/SIGQUIT shutdown, SIGPIPE ignored behavior, handler removal after normal teardown, removal with wrong session pointer warning, and coexistence when a signal had a non-default handler before setup.
