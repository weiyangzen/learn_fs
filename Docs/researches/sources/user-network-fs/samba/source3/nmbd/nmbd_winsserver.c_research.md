# sources/user-network-fs/samba/source3/nmbd/nmbd_winsserver.c

## Purpose
`nmbd_winsserver.c` implements Samba nmbd's WINS server. It stores WINS records in `wins.tdb`, imports/exports legacy `wins.dat`, handles registration/refresh/query/release/multihomed packets, maintains WINS lifecycle states, invokes optional hooks, and periodically ages and writes the database.

## Important APIs, types, and functions
- TDB conversion helpers: `wins_record_to_name_record`, `name_record_to_wins_record`, `name_to_key`.
- Storage APIs: `find_name_on_wins_subnet`, `wins_store_changed_namerec`, `add_name_to_wins_subnet`, `remove_name_from_wins_namelist`.
- Initialization/routing: `initialise_wins`, `packet_is_for_wins_server`.
- Request handlers: `wins_process_name_refresh_request`, `wins_process_name_registration_request`, `wins_process_multihomed_name_registration_request`, `wins_process_name_query_request`, `wins_process_name_release_request`.
- Maintenance: `fetch_all_active_wins_1b_names`, `initiate_wins_processing`, `wins_write_name_record`, `wins_write_database`.

## Control flow
Startup opens `wins.tdb`, stores a version, adds Samba self names, and imports live `wins.dat` rows. Packet routing selects unicast WINS requests. Refresh updates or re-registers records. Registration enforces static-name protection, group/unique policy, special 0x1c/0x1d behavior, WACK/query conflict challenges, and creation. Multihomed registration can add IPs after owner checks. Queries return active records, special `*<1b>` lists, or DNS proxy fallback. Releases validate ownership and transition records toward released state.

## State and persistence behavior
The authoritative store is `wins_tdb`; `wins_server_subnet->namelist` holds temporary fetched records and special traversals. Records include flags, source, death/refresh times, version id, owner IP, WINS state flags, and IP arrays. `wins_hook` stores changes and may run an external command. Periodic processing moves active, released, tombstoned, and deleted states and writes `wins.dat` in a background child.

## Dependencies and integration points
The file depends on TDB, Samba name-list operations, packet reply helpers, name-query helpers, async DNS proxying, loadparm WINS/TTL/hook settings, state-path helpers, child handling, and subnet globals.

## Risks and edge cases
Binary TDB packing/key encoding must remain stable. `name_to_key` uses a static buffer. Temporary TDB-fetched records require careful `data.ip` freeing. 0x1c lists are capped to avoid oversized replies while preserving 0x1b addresses. WACK conflict resolution locks packets across async callbacks. Hook execution is security-sensitive.

## Test signals
Cover TDB serialization, `wins.dat` import/export, unique/group/0x1c/0x1d registration, refresh ownership changes, conflict WACK paths, multihomed additions, `*<1b>` queries, DNS fallback, release transitions, aging, hook gating, and multi-IP response sizing.
