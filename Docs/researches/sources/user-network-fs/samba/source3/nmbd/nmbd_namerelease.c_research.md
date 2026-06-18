# sources/user-network-fs/samba/source3/nmbd/nmbd_namerelease.c

## Purpose
Implements asynchronous release of Samba-owned NetBIOS names from broadcast subnets and WINS. It sends release packets for all IPs associated with a name, handles WINS tag groups, and updates local namelists.

## Important APIs, Types, And Functions
Public API is `release_name()`. Internal functions are `release_name_response()`, `release_name_timeout_response()`, and `wins_release_name()`. It uses release callbacks, `queue_release_name()`, WINS tag helpers, and `standard_success_release()`.

## Control Flow
`release_name()` only releases active `SELF_NAME` records, marks `NB_DEREG`, then sends WINS or broadcast release packets for every IP. Caller callbacks are attached only to the final queued release. Responses validate answer/question names, ignore broadcast replies, handle WACK delays, treat nonzero rcode as failure, and on success call caller success plus `standard_success_release()`. Timeouts are always considered success; WINS timeout also marks the server temporarily dead.

## State And Persistence
Changes include `NB_DEREG`, response retry state, WINS liveness, and removal of released IPs from local name records. Records are deleted when no IPs remain.

## Dependencies, Risks, And Test Signals
Used by LMB demotion, WINS shutdown, and browser cleanup. Depends on namelist release callbacks, packet queues, and WINS tags. Risks include successful local cleanup despite unprocessed WINS release and final-packet-only callback semantics. Test signals include multi-IP release packet count, WACK delay, WINS rcode failure callback, timeout cleanup, and WINS server death marking.
