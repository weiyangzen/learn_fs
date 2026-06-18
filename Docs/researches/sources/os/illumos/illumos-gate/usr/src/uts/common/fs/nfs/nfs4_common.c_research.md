# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_common.c

## Purpose
Small common NFSv4 client/server support module. It defines the loadable filesystem wrapper for `nfs4`, transfer-size defaults, mount option updates, seqid response rules, retryable RPC errors, and stringification helpers for diagnostics.

## Module Registration
- `nfs4_ctags[]` holds the global tag list initialized from `NFS4_TAG_INITIALIZER`.
- `vfw4` defines the NFSv4 VFS with name `nfs4`, init function `nfs4init`, and flags `VSW_CANREMOUNT | VSW_NOTZONESAFE | VSW_STATS`.
- `modlfs4` registers the module as `"network filesystem version 4"`.

## Transfer Sizes
Defaults:
- `nfs4_max_transfer_size`: 32 KiB
- `nfs4_max_transfer_size_cots`: 1 MiB
- `nfs4_max_transfer_size_rdma`: 1 MiB

Functions:
- `nfs4tsize()` returns the generic default.
- `nfs4_tsize()` chooses transfer size from client `knetconfig` semantics: COTS/COTS_ORD and RDMA get larger defaults.
- `rfs4_tsize()` performs analogous sizing from server transport request type.

## Mount Option Updates
`nfs4_setopts()` applies user mount arguments to `mntinfo4_t`:
- Sets flags for `NOAC`, `NOCTO`, local locking, and group-id inheritance.
- Purges attribute cache immediately for `NOAC`.
- Validates and applies retransmission count and timeout.
- Clamps read/write transfer sizes to requested `rsize`/`wsize`.
- Applies attribute-cache min/max options for regular files and directories, converting seconds to high-resolution time and clamping to maximums.
- Returns `EINVAL` for invalid negative/zero values where required.

## Seqid Response Semantics
`nfs4_need_to_bump_seqid()` inspects a compound response. If it contains a seqid-dependent operation (`CLOSE`, `OPEN`, `OPEN_CONFIRM`, `OPEN_DOWNGRADE`, `LOCK`, `LOCKU`), it decides whether the caller should advance the seqid after the response. It does not bump for status values such as stale clientid/stateid, bad stateid, bad seqid, bad XDR, old stateid, resource, or no filehandle. All other statuses for seqid-dependent operations cause a bump.

## Retryable RPC Errors
`nfs4_rpc_retry_error()` returns true for transient transport/network errors:
- `ETIMEDOUT`
- `ECONNREFUSED`
- `ENETDOWN`
- `ENETUNREACH`
- `ENETRESET`
- `ECONNABORTED`
- `EHOSTUNREACH`
- `ECONNRESET`

## Diagnostic String Helpers
`nfs4_stat_to_str()` maps many `nfsstat4` values to stable strings and falls back to `"Unknown error %d"`.

`nfs4_recov_action_to_str()` maps recovery actions such as stale, failover, clientid, open files, wrongsec, expired, bad stateid, badhandle, bad seqid, grace, delay, lost lock, lost state request, and moved.

`nfs4_op_to_str()` maps NFSv4 operation numbers to strings using `REAL_OP4(op)` so pseudo/client operation encodings still resolve to the underlying protocol operation. Unknown operations produce `"Unknown op %d"`.

## Notable Details
- `nfs4_stat_to_str()` returns `"NFSS4ERR_NOTEMPTY"` for `NFS4ERR_NOTEMPTY`, which appears to include an extra `S` compared with the enum spelling.
- The source contains duplicated unreachable/redundant lines in two places: a repeated negative `retrans` check in `nfs4_setopts()` and a second `return ("NFS4ERR_DQUOT");` immediately after the first.
