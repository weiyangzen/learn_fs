# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_dfs.c

## Role

Implements SMB DFS referral handling for the kernel SMB server, including SMB2 DFS FSCTL dispatch and shared referral response encoding used by SMB1 transaction callers.

## Major Responsibilities

- Handles `FILE_DEVICE_DFS` FSCTL requests on IPC tree connections.
- Enforces SMB2 DFS capability checks and returns protocol-specific DFS errors.
- Decodes `FSCTL_DFS_GET_REFERRALS` and `FSCTL_DFS_GET_REFERRALS_EX` request bodies.
- Classifies referral paths as domain, DC, SYSVOL, root, link, or invalid.
- Calls user space over the SMB door interface to obtain configured DFS referral data.
- Encodes DFS referral response headers and referral entries for versions 1, 2, 3, and 4.
- Handles output buffer limits by returning overflow when no target fits and silently dropping later targets that do not fit.

## Key Functions

- `smb_dfs_fsctl()` validates IPC/DFS capability state and dispatches DFS FSCTL control codes.
- `smb_dfs_get_referrals()` decodes classic referral requests and writes encoded referrals to the FSCTL output mbuf chain.
- `smb_dfs_get_referrals_ex()` decodes the extended referral request fixed and variable parts, ignoring site data.
- `smb_dfs_get_reftype()` parses UNC paths and determines the DFS referral type.
- `smb_dfs_referrals_get()` uses `smb_kdoor_upcall()` with `SMB_DR_DFS_GET_REFERRALS` to query user-space DFS configuration.
- `smb_dfs_encode_hdr()` writes `PathConsumed`, target count, and response flags.
- `smb_dfs_encode_refv1()`, `smb_dfs_encode_refv2()`, and `smb_dfs_encode_refv3x()` encode version-specific referral entries.
- `smb_dfs_encode_targets()` appends DFS path, alternate path, and target UNC strings.
- `smb_dfs_referrals_free()` releases XDR-allocated referral response data.
- `smb_dfs_referrals_unclen()` computes encoded Unicode target UNC lengths.

## Research Notes

The kernel owns protocol decoding and referral packet layout, while actual DFS namespace knowledge comes from user space. Non-DC root behavior is explicit: domain/DC referral requests are rejected as invalid and SYSVOL referrals return no such device.
