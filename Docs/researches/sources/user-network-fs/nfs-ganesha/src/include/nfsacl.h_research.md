# sources/user-network-fs/nfs-ganesha/src/include/nfsacl.h

## Purpose

`nfsacl.h` defines the NFSACL v3 auxiliary RPC protocol data structures for POSIX ACL get/set support over NFSv3. It is a version-controlled mix of rpcgen-generated and hand-edited text.

## Important APIs, Types, and Functions

Mask constants include `NFS_ACL`, `NFS_ACLCNT`, `NFS_DFACL`, `NFS_DFACLCNT`, `NFS_ACL_MASK`, and `NFS_DFACL_MASK`. Types include `attr3`, `posix_acl_entry`, flexible `posix_acl`, `getaclargs`, `getaclresok`, `getaclres`, `setaclargs`, `setaclresok`, and `setaclres`. Program constants are `NFSACLPROG`, `NFSACL_V3`, `NFSACLPROC_NULL`, `NFSACLPROC_GETACL`, and `NFSACLPROC_SETACL`. XDR declarations cover every type.

## Control Flow

NFSACL dispatch decodes `getaclargs` or `setaclargs`, converts ACL wire entries to/from FSAL/POSIX ACL representations via protocol tools, executes ACL operations, and returns status plus optional attributes and access/default ACL arrays.

## State and Persistence Behavior

The header defines wire objects only. Persistent ACL state is stored by the underlying filesystem/FSAL after SETACL; GETACL returns snapshots of that state. Variable-size ACL arrays require careful allocation/free.

## Dependencies and Integration Points

It depends on `<rpc/rpc.h>` and on NFSv3 types from `nfs23.h` being available in including contexts. It integrates with `nfs_proto_data.h`, NFSACL service handlers/free functions, POSIX ACL conversion in `nfs_proto_tools.h`, export ACL options, and FSAL ACL operations.

## Risks and Test Signals

Risks include flexible array allocation mistakes, access/default ACL count mismatches, mask interpretation errors, status-to-attribute union misuse, missing include order for NFSv3 types, and memory leaks in XDR free paths. Tests should XDR round-trip GETACL/SETACL, encode/decode access and default ACLs, reject malformed counts/masks, verify directory vs non-directory default ACL behavior, and run NFSv3 ACL conformance against ACL-capable and ACL-disabled exports.
