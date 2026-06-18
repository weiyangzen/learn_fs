# sources/user-network-fs/samba/source3/winbindd/idmap_passdb.c

## Purpose
This small backend delegates mapping entirely to Samba passdb. It maps Unix IDs to SIDs with `pdb_id_to_sid` and SIDs to Unix IDs with `pdb_sid_to_id`.

## Important APIs, Types, And Functions
The backend methods are `idmap_pdb_init`, `idmap_pdb_unixids_to_sids`, and `idmap_pdb_sids_to_unixids`. `idmap_passdb_init` registers the backend under `passdb`.

## Control Flow
Initialization is a no-op returning OK. For Unix-ID-to-SID, each requested map is marked `ID_UNMAPPED`, then promoted to `ID_MAPPED` if passdb returns a SID. For SID-to-Unix-ID, each map is marked mapped or unmapped based on `pdb_sid_to_id`.

## State And Persistence
This file holds no state. Persistent identity information comes from the configured passdb backend.

## Dependencies And Integration
It includes `passdb.h` and the idmap interface. It is useful where Samba account database state is authoritative for local mappings.

## Risks And Test Signals
Tests should cover both mapping directions for users and groups, missing passdb records, passdb backend errors exposed as boolean failures, and mixed arrays where some records map and others do not. The functions always return `NT_STATUS_OK`, so callers must inspect per-map statuses.
