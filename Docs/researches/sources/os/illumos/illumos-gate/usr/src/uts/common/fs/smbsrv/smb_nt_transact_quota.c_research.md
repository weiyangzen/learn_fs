# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_transact_quota.c

## Summary
Implements SMB1 NT transact quota query and set operations for trees with quota support enabled.

## Main Responsibilities
- Validates tree quota feature availability.
- Decodes query parameters for SID list, start SID, restart, and single-entry behavior.
- Builds quota root paths from the tree root mount path.
- Initializes and frees quota SID lists and quota response data.
- Encodes quota query results and resume state.
- Restricts quota setting to administrators.
- Decodes and submits quota set records.

## Key APIs
- `smb_nt_transact_query_quota()`.
- `smb_nt_transact_set_quota()`.

## Important Behavior
Query requires exactly 16 parameter bytes and rejects requests that specify both SID list and start SID. It chooses `SMB_QUOTA_QUERY_SIDLIST`, `SMB_QUOTA_QUERY_STARTSID`, or `SMB_QUOTA_QUERY_ALL`, computes maximum response capacity, initializes SIDs from request data, calls `smb_quota_query()`, and encodes returned quotas.

`NT_STATUS_NO_MORE_ENTRIES` is converted to warning status plus successful completion with zero returned length, and the ofile quota resume SID is cleared.

Set quota requires exactly 2 parameter bytes, an admin user, a disk ofile, and a decoded quota list. It submits the list to `smb_quota_set()` and returns only status.

## Dependencies
Depends on quota feature flags, user admin checks, ofile lookup, `smb_node_getmntpath()`, quota XDR/free helpers, mbuf-chain quota encoders/decoders, and per-ofile quota resume storage.

## Risks
The quota root path is derived from the tree root mount path, so quota behavior follows the mounted filesystem boundary rather than arbitrary share path semantics.

The set path returns `-1` for non-admin access instead of the usual `SDRC_ERROR`, matching local convention only if dispatch treats nonzero as error.
