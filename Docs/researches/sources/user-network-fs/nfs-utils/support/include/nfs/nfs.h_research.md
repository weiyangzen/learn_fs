# sources/user-network-fs/nfs-utils/support/include/nfs/nfs.h

## Purpose
Defines generic NFS protocol limits, version/protocol bit helpers, and length-tagged NFS filehandle storage.

## Important APIs, Types, and Functions
`struct nfs_fh_len`, `NFS3_FHSIZE`, version/minor constants, and `NFSCTL_*` macros for protocol/version bitsets.

## Control Flow
Callers manipulate integer bitsets to enable/disable NFS versions, minor versions, UDP/TCP, and defaults. Filehandle users carry size plus bytes.

## State and Persistence Behavior
No state. Bitsets are caller-owned and may persist in daemon configuration or kernel setup commands.

## Dependencies and Integration Points
Includes Linux types, RPC NFSv2 protocol declarations, and export flags. Used across mountd/nfsdctl/export support.

## Risks and Edge Cases
Macros mutate arguments, so side effects in macro arguments are unsafe. Minor-version default comments must match bit values.

## Test Signals
Test bitset set/unset/is-set operations, default masks, any-protocol checks, and filehandle size bounds.
