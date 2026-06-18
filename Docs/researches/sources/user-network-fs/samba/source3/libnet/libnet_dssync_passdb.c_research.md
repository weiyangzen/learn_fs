# sources/user-network-fs/samba/source3/libnet/libnet_dssync_passdb.c

## Purpose

Implements a DSSync backend that imports replicated users and groups into Samba passdb, group mapping, and local Unix account/group membership state.

## Important APIs, Types, and Functions

Exports `libnet_dssync_passdb_ops`. Internal state types are `dssync_passdb`, `dssync_passdb_obj`, and `dssync_passdb_mem`. Object handlers include `handle_account_object`, `handle_alias_object`, `handle_group_object`, and a not-implemented trust handler. `sam_account_from_object` maps DRS attributes into `struct samu`. `find_drsuapi_attr_*` helpers and `GET_*` macros decode replicated attributes.

## Control Flow

Startup selects a passdb backend and creates in-memory RBT indexes. Object processing stores each supported object by GUID and dispatches by `sAMAccountType`. Account handling ensures a Unix account exists using configured add scripts, then adds or updates the Samba account with SID/rid, names, profile fields, logon data, logon hours, counters, hashes, domain, and flags. Group and alias handlers create Unix groups and passdb mappings and stage member links. Linked attributes stage active/inactive membership records. Finish traverses staged aliases/groups to update alias membership and Unix group membership.

## State and Persistence Behavior

In-memory RBT databases hold object and membership pointers for the duration of a run. Persistent effects include passdb writes, group mapping changes, Unix user/group creation, primary group changes, alias member changes, and Unix group member edits. This backend does not persist UTDV.

## Dependencies and Integration Points

Integrates DRSUAPI objects with passdb APIs, dbwrap RBT, local NSS, Samba add-user/add-machine scripts, group mapping, SID helpers, base64 userParameters encoding, and Unix group modification helpers.

## Risks and Test Signals

Risks are substantial because replicated input can create or modify local accounts. Pointer values are stored in process-local DB records, duplicate inserts abort, trust objects are unimplemented, password history/account expiry TODOs remain, and some group paths return errors for benign cases. Tests should isolate passdb/NSS and cover user add/update, group/alias creation, linked add/delete, missing members, distribution-group filtering, hash import, and script failures.
