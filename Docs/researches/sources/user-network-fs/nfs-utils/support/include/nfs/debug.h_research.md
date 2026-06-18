# sources/user-network-fs/nfs-utils/support/include/nfs/debug.h

## Purpose
Defines legacy debug bit masks for sunrpc, nfsd, lockd, and NFS client debug controls.

## Important APIs, Types, and Functions
Macros include `RPCDBG_*`, `NFSDDBG_*`, `NLMDBG_*`, `NFSDBG_*`, `CTL_SUNRPC`, and debug sysctl enum values.

## Control Flow
Consumers OR, set, or display bit flags for kernel debug facilities; no control flow is implemented here.

## State and Persistence Behavior
No runtime state. Values are ABI/configuration constants.

## Dependencies and Integration Points
Included by utilities that read or change kernel debug flags.

## Risks and Edge Cases
Values must match kernel expectations. Some sysctl paths are legacy and may be absent on modern kernels.

## Test Signals
Compile debug utilities and test setting/listing each debug facility against kernels with and without legacy sysctl support.
