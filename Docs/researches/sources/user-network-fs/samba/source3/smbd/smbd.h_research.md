# sources/user-network-fs/samba/source3/smbd/smbd.h

## Purpose
Central smbd header that pulls together VFS, generated prototypes, locking, file-handle, and SMB1-specific declarations. It also defines transaction state and flags for Unix path conversion behavior.

## Important APIs, Types, and Functions
`struct trans_state` tracks SMB transaction/trans2/nttrans aggregation: vuid, MID, return limits, command/call fields, setup words, accumulated parameter/data buffers, and completion behavior. Defines `UCF_POSIX_PATHNAMES`, `UCF_PREP_CREATEFILE`, `UCF_LCOMP_LNK_OK`, `UCF_GMT_PATHNAME`, and `UCF_DFS_PATHNAME` for `unix_convert`-style path processing.

## Control Flow
This header has no executable flow. It shapes compile-time inclusion for smbd modules, conditionally includes SMB1 server headers, and gives path-conversion callers shared flag constants.

## State and Persistence
`trans_state` instances are runtime request state, usually linked in per-connection lists and freed after transaction completion. The path flags are stateless compile-time constants.

## Dependencies and Integration Points
Includes `vfs.h`, `smbd/proto.h`, locking prototypes, share-mode locks, and fd handles. SMB1 includes are guarded by `WITH_SMB1SERVER`, making this header a compatibility aggregation point for older protocol code.

## Risks
Because this header is broad, changes can trigger widespread rebuilds and subtle include-order issues. Transaction buffer fields carry byte counts and pointers, so users must validate total/received lengths. Path flags intentionally reuse SMB flag bits for GMT and DFS pathnames, so accidental value changes can alter wire-visible behavior.

## Test Signals
Build both with and without `WITH_SMB1SERVER`. Exercise transaction request assembly and path conversion modes for POSIX, DFS, GMT, symlink-last-component, and create-file preparation cases.
