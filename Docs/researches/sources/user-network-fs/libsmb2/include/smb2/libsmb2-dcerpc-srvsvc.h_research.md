# sources/user-network-fs/libsmb2/include/smb2/libsmb2-dcerpc-srvsvc.h

## Purpose
`libsmb2-dcerpc-srvsvc.h` defines SRVSVC DCERPC share enumeration and share-info structures, plus high-level share enumeration helpers.

## Important APIs, Types, and Functions
It declares SRVSVC opnums `SRVSVC_NETRSHAREENUM` and `SRVSVC_NETRSHAREGETINFO`, share type flags, `enum SHARE_INFO_enum`, share info levels 0/1/2 and containers, request/reply structs for `NetrShareEnum` and `NetrShareGetInfo`, coder functions for each structure, and `smb2_share_enum_async()`/`smb2_share_enum_sync()`.

## Control Flow
The async helper requires an IPC$ connection, encodes a `NetrShareEnum` request at the chosen info level, calls SRVSVC over DCERPC, and reports a decoded `srvsvc_NetrShareEnum_rep` through the callback. The sync helper wraps the async flow and returns the reply pointer or NULL.

## State and Persistence Behavior
Share enumeration results are transient decoded arrays of UTF-16-backed share names, remarks, paths, and counters. Callers must free successful results using `smb2_free_data()`.

## Dependencies and Integration Points
It includes `libsmb2-dcerpc.h` and integrates with IPC$ tree connections and DCERPC transport setup. `libsmb2.h` includes this header for compatibility.

## Risks and Edge Cases
The API only works on IPC$ and requires suitable server permissions. Level-specific unions must be decoded according to `Level`; misuse can read the wrong union member. Large share lists may require resume handling.

## Test Signals
Run level 0, 1, and 2 enumeration against servers with normal, hidden, IPC, printer, and administrative shares. Test permission-denied, empty list, resume handle, and proper `smb2_free_data()` cleanup.
