# sources/user-network-fs/samba/source3/smbd/notifyd/notifydd.c

## Purpose
`notifydd.c` is a standalone notify daemon executable used for development or testing. It initializes Samba configuration, logging, tevent, messaging, and then runs `notifyd_send()`.

## Important APIs, Types, and Functions
The only function is `main()`. It uses `loadparm_init_s3()`, `lp_load_initial_only()`, `samba_tevent_context_init()`, `messaging_init()`, `lp_load_global()`, `messaging_ctdb_connection()`, `notifyd_send()`, `tevent_req_poll_unix()`, and `notifyd_recv()`.

## Control Flow
Startup enables a full talloc leak report, creates a stack frame, initializes loadparm, sets stdout logging at debug level 10, loads the Samba config, creates the event and messaging contexts, reloads global config, starts notifyd with the CTDB messaging connection and no explicit system watcher callback, then polls the notifyd request until it exits. Since `notifyd_send()` substitutes a dummy watcher when the callback is null, this binary runs the message daemon without real filesystem backend watches unless changed by the caller.

## State and Persistence
State is process-local and under the talloc stack frame. The program registers the notify daemon name through `notifyd_send()` and keeps running until the tevent request completes or errors.

## Dependencies and Integration Points
It depends on notifyd, Samba CTDB messaging support, tevent Unix helpers, and Samba parameter loading. `wscript_build` defines it as a non-installed `notifydd` binary.

## Risks and Edge Cases
The executable exits with status 1 on initialization failures but prints notifyd terminal status and returns 0 after `notifyd_recv()`, even if that status is nonzero. Forced debug level 10 can produce large logs. Passing null system watch arguments means behavior differs from production smbd integration with inotify.

## Test Signals
Build coverage ensures the binary links. Runtime smoke testing can start `notifydd` with a valid smb.conf and verify that clients can find `"notify-daemon"` and exchange add/trigger messages.
