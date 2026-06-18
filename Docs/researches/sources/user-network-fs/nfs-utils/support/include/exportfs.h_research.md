# sources/user-network-fs/nfs-utils/support/include/exportfs.h

## Purpose
Defines the central export/client data model and function declarations shared by exportfs, mountd, auth, cache, and pseudo-root code.

## Important APIs, Types, and Functions
Key types are `nfs_client`, `nfs_export`, `exp_hash_entry`, `exp_hash_table`, `export_features`, and client class enums. Inline helpers get/set AF_INET/AF_INET6 address slots. It declares client, export, xtab, secinfo, hostname, feature, realpath, and export-test APIs.

## Control Flow
Implementation modules parse export entries into `nfs_export`, associate them with `nfs_client`, hash by path, match callers by addrinfo, and persist/read etab state. Inline address helpers hide union field access.

## State and Persistence Behavior
`exportlist` and `clientlist` are extern process-global tables. Export entries own dynamically allocated option fields and cached real paths; etab paths persist state on disk.

## Dependencies and Integration Points
Depends on `nfslib.h`, `sockaddr.h`, and libc networking headers. This is the primary integration header for support/export modules.

## Risks and Edge Cases
ABI and ownership expectations are implicit. Address setters silently ignore unsupported families. Bitfield state in `nfs_export` must stay consistent with etab/cache operations.

## Test Signals
Build all export modules, test client/export lifecycle, address helpers with IPv4/IPv6, etab read/write, feature probing, and duplicate/free paths.
