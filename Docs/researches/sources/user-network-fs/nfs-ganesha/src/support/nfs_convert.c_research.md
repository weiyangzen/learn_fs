# sources/user-network-fs/nfs-ganesha/src/support/nfs_convert.c

## Purpose
This file centralizes stringification and status conversion utilities for NFS protocol code. It maps NFS operation numbers, NFS status enums, FSAL status values, file types, request results, auth errors, and 64-bit host/network byte order conversions into protocol-facing representations.

## Important APIs, Types, And Functions
Key exports include `nfsproc3_to_str` when NFSv3 is enabled, `nfsop4_to_str`, `nfsstat3_to_str`, `nfsstat4_to_str`, `nfstype3_to_str`, `nfs_req_result_to_str`, `nfs_htonl64`, `nfs_ntohl64`, `auth_stat2str`, `nfs4_Errno_verbose`, and `nfs3_Errno_verbose` when NFSv3 is enabled. Static `op_names_v3` and `op_names_v4` tables rely on enum-indexed initializers and name prefixes.

## Control Flow
Operation string conversion indexes a static table and strips fixed prefixes (`NFSPROC3_` and `OP_`) after range checks. Status and type conversions are large switch statements returning string literals. FSAL-to-NFS conversion switches on `status.major`, maps each FSAL error to a protocol status, and logs critical diagnostics for non-retryable IO-like cases that are collapsed to protocol IO errors.

## State And Persistence
The file has no mutable state and no persistence. All outputs are string literals, converted integers, or status enum values.

## Dependencies And Integration Points
It includes protocol headers `nfs23.h`, `nfs4.h`, `mount.h`, and `nfs_convert.h`. It is used broadly by request handling, logging, filehandle management, FSAL error handling, duplicate request reporting, and RPC authentication diagnostics.

## Risks And Test Signals
Risks include enum drift when new NFSv4 operations or errors are added without updating tables/switches, unknown values collapsing to `ILLEGAL` or generic strings, and `LITTLEEND` compile-time dependence for 64-bit byte swapping. Since many functions return non-const `char *` despite literals, callers must not mutate the result. Tests should include every known enum value, out-of-range operation numbers, representative FSAL error mappings for v3 and v4, and endian conversion round trips.
