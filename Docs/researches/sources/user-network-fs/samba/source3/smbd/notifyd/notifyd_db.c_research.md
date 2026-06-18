# sources/user-network-fs/samba/source3/smbd/notifyd/notifyd_db.c

## Purpose
This file provides a public database-walk helper for clients that need to inspect notifyd's current registrations. It asks the running notify daemon for a marshalled database snapshot and calls a user callback for every stored notify instance.

## Important APIs, Types, and Functions
`notify_walk()` is the exported API. `notifyd_parse_db()` validates the returned buffer, extracts the leading replication log index, and parses the dbwrap-marshalled payload. `notifyd_parse_db_parser()` converts each key to a nul-terminated path, parses the entry value with `notifyd_parse_entry()`, and invokes the caller callback for each `notifyd_instance`.

## Control Flow
`notify_walk()` finds `"notify-daemon"` in the messaging names db, creates a private tevent context, starts a `messaging_read_send()` for `MSG_SMB_NOTIFY_DB`, sets a 10-second end time, sends `MSG_SMB_NOTIFY_GET_DB`, polls until a response, receives one `messaging_rec`, and parses it. Parsing skips malformed individual records by logging and returning true, but a malformed outer marshalling buffer returns an error status.

## State and Persistence
No local persistent state is created. The snapshot includes notifyd's marshalled in-memory rbt database prefixed by an 8-byte log index. The parsed `log_idx` is not returned to callers, so the helper is for inspection, not synchronization.

## Dependencies and Integration Points
It depends on Samba messaging, server-id name lookup, tevent, dbwrap marshalling parser, `notifyd_private.h`, and `notifyd.h`. `test_notifyd.c` uses it to check whether the current messaging server id appears in notifyd's db.

## Risks and Edge Cases
The helper blocks by polling a tevent request up to 10 seconds, which is acceptable for tests/admin inspection but not for hot paths. It trusts notifyd's native db representation and therefore inherits alignment and ABI assumptions from `notifyd_entry.c`. If no daemon is registered it returns `NT_STATUS_SERVER_UNAVAILABLE`.

## Test Signals
`test_notifyd_dbtest1` calls `notify_walk()` before and after canceling a wait request to assert that the local client appears and then disappears. Additional useful tests would cover timeout, no daemon, corrupt db payload, and multiple instances under one path.
