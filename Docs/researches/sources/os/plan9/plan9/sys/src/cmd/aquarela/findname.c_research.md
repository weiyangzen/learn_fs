# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/findname.c

Implements NBNS name query through `nbnsfindname`.

Key behavior:
- Builds a name query request with `nbnsmessagenamequeryrequestnew`.
- Uses an `Alt` over timeout and transaction response channels.
- Retries broadcast/unicast queries.
- On success, extracts IPv4 address from NB resource rdata and converts it to Plan 9 IPv6-format IP storage.
- Optionally returns TTL.

Interactions:
- Used by `nbresolve.c` before DNS fallback.
- Shares retry/transaction/alarm flow with `addname.c`.

Notable details:
- Requires an answer record; no answer is treated as failure even if rcode is zero.
