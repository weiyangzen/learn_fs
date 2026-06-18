# sources/user-network-fs/samba/source3/nmbd/nmbd_namequery.c

## Purpose
Implements asynchronous NetBIOS name query initiation, response handling, timeout handling, and local short-circuit lookup. It is the common query layer for browser role transitions, WINS discovery, and other name resolution.

## Important APIs, Types, And Functions
Public APIs are `query_name()` and `query_name_from_wins_server()`. Internal functions are `query_name_response()`, `query_name_timeout_response()`, and `query_local_namelists()`. It uses query callback typedefs, `response_record`, fabricated `res_rec` values for local hits, and queue helpers.

## Control Flow
`query_name()` builds an `nmb_name`, checks lmhosts and the local subnet namelist first, and if found fabricates a resource record and calls success immediately. Otherwise it queues a network query. `query_name_from_wins_server()` queues a directed WINS-server query. Response handling suppresses retries, handles WACK by delaying, treats nonzero rcode as failure, extracts the first answer IP, and only invokes callbacks for the first response. Timeout calls failure only if no response was seen.

## State And Persistence
Mutates response-record retry fields and removes response records on completion. It does not cache network query answers in namelists.

## Dependencies, Risks, And Test Signals
Depends on lmhosts, namelist lookup, packet queueing, and WINS query helpers. Risks include callback reentrancy from local hits, stale WACK-delayed records, and reducing multi-IP answers to one callback IP. Test signals include lmhosts/local success, network positive/negative responses, WACK delay, timeout failure, duplicate response logging without duplicate callbacks, and directed WINS queue failures.
