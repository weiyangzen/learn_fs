<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_traceid.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_traceid.c

## Purpose
This file wires Samba debug trace IDs into tevent callbacks so asynchronous winbind event handling preserves request correlation in logs.

## Important APIs, Types, And Functions
`winbind_debug_traceid_setup()` registers trace callbacks for tevent loop, fd, signal, timer, immediate, and queue events. Each event-specific callback stores `debug_traceid_get()` as an event tag on attach and restores that tag with `debug_traceid_set()` before handler execution.

## Control Flow
On setup, all tevent trace callbacks are installed and trace ID is initialized to 1, representing out-of-request execution. When events are attached, the current trace ID is copied into the event tag. Before a handler runs, the tag is copied back into the active debug trace ID. After a loop iteration, `debug_traceid_trace_loop()` resets the active ID to 1.

## State And Persistence Behavior
State is held in tevent event tags and the process-local debug trace ID. There is no persistent storage. The reset-to-1 behavior prevents one request handler's trace ID from bleeding into unrelated loop work.

## Dependencies And Integration Points
It depends on `lib/util/debug.h`, tevent trace APIs, and the header `winbindd_traceid.h`. It integrates during winbind event loop initialization.

## Risks And Test Signals
Risks are trace callback ordering changes in tevent, missing coverage for a new event type, or accidental reset while nested callbacks still need request context. Good signals are debug-log correlation tests across timers, fd events, queue entries, and idle loop boundaries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_traceid.c -->
