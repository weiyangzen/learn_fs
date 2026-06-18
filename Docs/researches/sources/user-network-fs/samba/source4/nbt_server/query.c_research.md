# sources/user-network-fs/samba/source4/nbt_server/query.c

## Purpose

`query.c` answers NetBIOS name query requests or forwards them to WINS when recursion is requested and local answers are unavailable or special WINS behavior is needed.

## Important APIs, Types, and Functions

The file exports `nbtd_request_query()`. It uses `nbtd_query_status()` for status queries, `nbtd_find_iname()` for local name lookup, `nbtd_winsserver_request()` for recursive/WINS handling, `nbtd_negative_name_query_reply()`, `nbtd_name_query_reply()`, and `nbtd_address_list()`.

## Control Flow

Status queries with `NBT_QTYPE_STATUS` are delegated immediately. Normal queries validate one NetBIOS/IP question, find a matching local interface name, and if absent either suppress negative replies for broadcasts, forward recursive queries to WINS, or send a negative reply. Existing group names on a WINS server may also be forwarded for non-broadcast recursive queries. Inactive names are ignored for broadcast queries. Otherwise the file replies with the name's TTL, flags, and interface-prioritized address list.

## State and Persistence Behavior

No persistent state is written. The function reads the in-memory name list and loadparm WINS-server role. Sent packets update stats in packet helpers.

## Dependencies and Integration Points

Dependencies include NBT packet structures, WINS server request handling, node status handling, interface address-list construction, and loadparm.

## Risks and Test Signals

Risks include WINS recursion branching for group names, no negative replies to broadcasts, inactive name suppression, and exact matching rules in `nbtd_find_iname()`. Tests should query active unique names, active group names with WINS enabled, missing names with broadcast/recursion/no-recursion combinations, inactive names, and node status queries.
