# sources/user-network-fs/samba/source4/rpc_server/unixinfo/dcesrv_unixinfo.c

## Purpose

This file implements the Samba `unixinfo` DCE/RPC endpoint. It translates between Windows SIDs and Unix UID/GID values using winbind ID mapping, and exposes a small passwd lookup call that returns home directory and shell data for requested UIDs.

## Important APIs, Types, And Functions

`dcesrv_unixinfo_SidToUid()` maps one SID to an `id_map` with `wbc_sids_to_xids()` and accepts `ID_TYPE_UID` or `ID_TYPE_BOTH`. `dcesrv_unixinfo_UidToSid()` validates that the incoming 64-bit UID fits in 32 bits, prepares an `ID_TYPE_UID` mapping, and calls `wbc_xids_to_sids()`. `dcesrv_unixinfo_SidToGid()` mirrors SID-to-UID but accepts `ID_TYPE_GID` or `ID_TYPE_BOTH`. `dcesrv_unixinfo_GidToSid()` mirrors UID-to-SID for groups. `dcesrv_unixinfo_GetPWUid()` loops over input UIDs, calls `getpwuid()`, and returns per-entry homedir, shell, and NTSTATUS.

## Control Flow

Each mapping call allocates one `struct id_map`, initializes the SID or xid side, calls the relevant winbind client helper, propagates helper failures, and then validates the returned ID type. UID/GID-to-SID calls explicitly reject values that do not round-trip through `uint32_t`. `GetPWUid` preallocates an output array sized to the input count, sets output count to match, then fills each entry independently so missing users or allocation failures are reported per UID rather than failing the whole call.

## State And Persistence

The endpoint does not persist state. It queries winbind/idmap state and the system passwd database at call time. Output arrays and copied strings are per-call talloc allocations. `getpwuid()` may use process-global libc/NSS state, but this file stores none of it.

## Dependencies And Integration Points

The file integrates generated `ndr_unixinfo` dispatch, Samba DCE/RPC call handling, winbind client ID mapping (`wbc_sids_to_xids()` and `wbc_xids_to_sids()`), SID/idmap structures, libc/NSS passwd lookup through `getpwuid()`, and generated `ndr_unixinfo_s.c`.

## Risks And Edge Cases

ID type validation is important because SID mappings can be UID-only, GID-only, both, or unknown. UID/GID truncation checks prevent silently mapping IDs outside the 32-bit Unix ID range accepted by the RPC structures. `getpwuid()` is not reentrant and can be affected by NSS configuration or blocking directory backends. Large input counts allocate proportional memory. Missing passwd entries are not fatal, which clients must handle from per-entry status.

## Test Signals

Useful tests include SID-to-UID/GID mappings for UID-only, GID-only, BOTH, unknown, and unmapped SIDs; UID/GID-to-SID for valid and out-of-range IDs; winbind failure propagation; `GetPWUid` with existing, missing, and mixed UID lists; and NSS-backed integration tests confirming home directory and shell strings are copied under the response memory context.
