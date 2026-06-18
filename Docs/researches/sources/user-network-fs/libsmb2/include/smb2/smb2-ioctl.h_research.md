# sources/user-network-fs/libsmb2/include/smb2/smb2-ioctl.h

## Purpose
`smb2-ioctl.h` defines additional Windows/SMB filesystem control codes for use with SMB2 IOCTL requests.

## Important APIs, Types, and Functions
It defines `FSCTL_*` constants for object IDs, reparse points, duplicate extents, filesystem statistics, trim, compression, NTFS/ReFS volume data, retrieval pointers, sparse/zero data, pipe operations, allocated ranges, offload read/write, integrity, encryption, USN, and snapshot enumeration. It aliases `FSCTL_GET_SHADOW_COPY_DATA` to `FSCTL_SRV_ENUMERATE_SNAPSHOTS`.

## Control Flow
No runtime code exists. Callers place these constants in `struct smb2_ioctl_request.ctl_code` and submit through raw IOCTL APIs.

## State and Persistence Behavior
The header has no state. Specific IOCTLs can query or mutate remote filesystem metadata when used by callers.

## Dependencies and Integration Points
It complements `smb2.h`, which defines core SMB2 IOCTL structs and a smaller set of `SMB2_FSCTL_*` constants. It is not listed in the autotools install header list in `include/Makefile.am`.

## Risks and Edge Cases
The license comment uses curly quotes and the author email appears misspelled. Constant names omit the `SMB2_` prefix used in `smb2.h`, so collision with platform headers is possible. Install/build metadata may not expose this header consistently.

## Test Signals
Compile downstream code including this header alone and with Windows headers. Exercise harmless query IOCTLs and validate server status for unsupported control codes.
