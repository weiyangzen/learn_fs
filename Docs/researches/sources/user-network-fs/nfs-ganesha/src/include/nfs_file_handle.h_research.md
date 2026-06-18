# sources/user-network-fs/nfs-ganesha/src/include/nfs_file_handle.h

## Purpose

`nfs_file_handle.h` provides allocation, validation, FSAL conversion, export-ID extraction, sanity checking, and logging helpers for NFSv3/NFSv4/NLM/NFSACL file handles.

## Important APIs, Types, and Functions

Inline helpers allocate/free fixed-size NFSv3 and NFSv4 buffers, compute actual and padded handle sizes, validate v4 lengths with optional v3-handle compatibility, test empty v4 handles, extract v3/NLM export IDs, and render file handles in debug logs. Public conversion/validation functions include `nfs3_FhandleToCache`, `nfs4_FSALToFhandle`, `nfs3_FSALToFhandle`, `nfs3_Is_Fh_Invalid`, `nfs4_Is_Fh_Invalid`, `nfs4_Is_Fh_DSHandle`, `nfs4_sanity_check_FH`, and `nfs4_sanity_check_saved_FH`.

## Control Flow

Protocol handlers allocate output handles, convert FSAL object handles to wire handles on lookup/create/getfh, validate inbound handles before dispatching operations, resolve handles to cache/export objects, and use sanity checks to enforce required object types and DS-handle permissions.

## State and Persistence Behavior

Allocated NFS handle buffers are request/result memory. The encoded handles persist at clients and refer to export/FSAL state. Logging macros read function descriptor arrays and component levels but do not mutate handle state.

## Dependencies and Integration Points

It depends on logging, display, SAL data, export manager, handle layout, and protocol function descriptors. It integrates with NFSv3, NFSv4 compound state, NLM, NFSACL, pNFS DS handles, and export lookup.

## Risks and Test Signals

Risks include missing allocation checks, incorrect padding compatibility, NULL handle logging, byte-order export ID extraction, invalid DS handle acceptance, and opaque logging buffer truncation. Tests should cover handle allocation/free, invalid length/version/flag combinations, export ID extraction, FSAL round trips, v3-for-v4 compatibility toggles, DS handle restrictions, and debug macro builds.
