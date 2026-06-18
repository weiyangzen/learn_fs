# sources/user-network-fs/samba/source3/nmbd/nmbd_winsproxy.c

## Purpose
`nmbd_winsproxy.c` implements WINS proxy behavior for broadcast name queries. It queries a configured WINS server on behalf of a broadcast client, caches successful answers on the original subnet, and replies when the real owner is not on the same broadcast subnet.

## Important APIs, types, and functions
- `make_wins_proxy_name_query_request` packages the original subnet/packet and starts a unicast WINS query.
- `wins_proxy_name_query_request_success` caches successful WINS answers and replies.
- `wins_proxy_name_query_request_fail` logs lookup failure.
- `wins_proxy_userdata_copy_fn` and `wins_proxy_userdata_free_fn` deep-copy and free the saved original packet.

## Control flow
The exported entry point builds userdata with copy/free hooks and calls `query_name` on `unicast_subnet`. On success, the callback extracts NB flags and IPs, adds a `WINS_PROXY_NAME` to the original broadcast subnet, suppresses a reply if a returned IP is on the requester's subnet, and otherwise replies to the saved packet with the returned resource data.

## State and persistence behavior
No disk state is persisted. The module mutates in-memory name-list cache entries on the original broadcast subnet. The saved packet is deep-copied and locked in userdata until response-record cleanup.

## Dependencies and integration points
It integrates with name querying, name-list insertion/lookup, packet replies, NetBIOS flag helpers, subnet masks, WINS client state, and response-record userdata ownership rules.

## Risks and edge cases
Multi-IP rdata must parse in six-byte chunks. Same-subnet suppression depends on correct subnet masks. The userdata union manually serializes pointers. Packet deep-copy/free must stay balanced.

## Test signals
Simulate successful and failed WINS responses, single/multi-IP rdata, same-subnet suppression, cache insertion as `WINS_PROXY_NAME`, and cleanup of saved packets.
