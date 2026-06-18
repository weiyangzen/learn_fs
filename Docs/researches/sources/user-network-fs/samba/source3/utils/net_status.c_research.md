# sources/user-network-fs/samba/source3/utils/net_status.c

## Purpose
Implements local `net status sessions` and `net status shares` views over active Samba runtime state, with human-readable and parseable outputs.

## Important APIs, Types, and Functions
`sessionid_traverse_read()` drives session output through `show_session()` and session collection through `collect_pids()`. `connections_forall_read()` drives share output through `show_share()` and `show_share_parseable()`. `process_exists()` filters stale process records.

## Control Flow
`net_status()` dispatches subcommands. Sessions parse optional `parseable`, print headers for human output, and traverse session records. Shares either print connection rows directly or collect sessions first so parseable output can join service connections to user/group/hostname data by server ID.

## State and Persistence
Read-only; consumes session and connection TDB-backed state and allocates a temporary session array for parseable share output.

## Dependencies and Integration Points
Depends on `session.h`, `conn_tdb.h`, server ID formatting, UID/GID name conversion, and common command dispatch.

## Risks
Runtime state can change during traversal. Parseable share output emits empty identity fields for guest/unmatched connections. Allocation failure in `collect_pids()` silently clears collected sessions.

## Test Signals
Cover sessions/shares in both output modes, dead-process filtering, guest/unmatched rows, invalid arguments, empty databases, and parseable delimiter stability.
