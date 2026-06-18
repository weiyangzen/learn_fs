# sources/user-network-fs/samba/source3/nmbd/nmbd_incomingrequests.c

## Purpose
Processes incoming NetBIOS name-service requests on port 137 for broadcast and local unicast behavior outside the WINS server path. It handles release, refresh, registration, node-status, and name-query requests.

## Important APIs, Types, And Functions
Public handlers are `process_name_release_request()`, `process_name_refresh_request()`, `process_name_registration_request()`, `process_node_status_request()`, and `process_name_query_request()`. Internal helpers are `send_name_release_response()`, `send_name_registration_response()`, and `status_compare()`.

## Control Flow
Release handling rejects unexpected unicast releases, ignores many non-owned broadcast releases, and sends `ACT_ERR` when another host tries to release a Samba-owned name. Refresh handling rejects unicast refreshes and logs broadcast refreshes. Registration handling rejects unicast registrations, removes stale WINS proxy records, rejects conflicts with Samba-owned names or group/unique incompatibility, and updates existing non-owned unique records. Node-status handling replies only for local self names and builds a filtered, sorted list of active self/permanent names. Name-query handling searches appropriate namelists, suppresses expired records, replies to allowed unicast/broadcast queries, launches WINS proxy lookup on configured misses, and avoids negative broadcast responses.

## State And Persistence
Mostly reads state, but can remove WINS proxy names, update remote unique name TTL/IP data, and trigger WINS proxy queries that later populate the namelist. Persistence is indirect through namelist change flags.

## Dependencies, Risks, And Test Signals
Depends on namelist APIs, WINS proxy query creation, `reply_netbios_packet()`, IP sorting, and configuration. Risks include packet structure assumptions, exact broadcast silence semantics, duplicate replies for WINS proxy names on the requester's subnet, and node-status size bounds. Test signals include ACT_ERR on owned-name release, no negative broadcast query replies, WINS proxy query creation, node-status filtering/sorting, and recursion-desired unicast behavior.
