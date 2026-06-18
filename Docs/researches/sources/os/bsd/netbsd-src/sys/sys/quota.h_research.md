# File Research: sources/os/bsd/netbsd-src/sys/sys/quota.h

## Purpose
Defines generic quota key/value ABI for quota records and semantic restriction flags.

## Main API
- ID types: `QUOTA_IDTYPE_USER`, `QUOTA_IDTYPE_GROUP`.
- Object types: `QUOTA_OBJTYPE_BLOCKS`, `QUOTA_OBJTYPE_FILES`.
- Special values: `QUOTA_DEFAULTID`, `QUOTA_NOLIMIT`, `QUOTA_NOTIME`.
- Restrictions: `QUOTA_RESTRICT_NEEDSQUOTACHECK`, `QUOTA_RESTRICT_UNIFORMGRACE`, `QUOTA_RESTRICT_32BIT`, `QUOTA_RESTRICT_READONLY`.
- Structures: `struct quotakey`, `struct quotaval`.

## Dependencies
Includes `sys/types.h`.

## Risks and Notes
The header separates billed entity (`quotakey`) from limit/usage value (`quotaval`). Restriction flags are hints for comprehensible diagnostics, not enforcement by themselves.
