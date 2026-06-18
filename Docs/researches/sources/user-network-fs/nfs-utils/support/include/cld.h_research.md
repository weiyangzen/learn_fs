# sources/user-network-fs/nfs-utils/support/include/cld.h

## Purpose
Defines the packed nfsdcld upcall ABI used for NFSv4 client tracking and reclaim decisions.

## Important APIs, Types, and Functions
`CLD_UPCALL_VERSION`, `NFS4_OPAQUE_LIMIT`, `enum cld_command`, `struct cld_name`, `struct cld_princhash`, `struct cld_clntinfo`, `struct cld_msg`, `struct cld_msg_v2`, and `struct cld_msg_hdr`.

## Control Flow
Kernel/userspace messages carry a version, command, status, xid, and command-specific union payload. Version 2 can include client name plus Kerberos principal hash.

## State and Persistence Behavior
No code executes here; the packed struct layout is the persistent wire/shared-memory contract between nfsd and nfsdcld.

## Dependencies and Integration Points
Depends on fixed-width integer types from consumers. Integrated by nfsdcld and kernel upcall handling.

## Risks and Edge Cases
Packed layout, signed status width, and opaque length limits must remain ABI-compatible. Version negotiation is required before using v2-only fields.

## Test Signals
Compile-time size/layout checks and integration tests for create/remove/check/grace/version upcalls across v1/v2 peers.
