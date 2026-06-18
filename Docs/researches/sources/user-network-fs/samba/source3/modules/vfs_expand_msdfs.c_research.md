# sources/user-network-fs/samba/source3/modules/vfs_expand_msdfs.c

## Purpose
`vfs_expand_msdfs.c` rewrites MSDFS referral targets containing `@mapfile@` based on client IP prefix mappings, allowing location-aware referral targets.

## Important APIs, Types, And Functions
`read_target_host()` scans a map file of `IP-prefix expansion` lines. `expand_msdfs_target()` parses the `@...@` mapfile segment, converts backslashes to slashes, gets the remote address, reads the replacement, applies Samba substitutions, and builds the new referral target. `expand_read_dfs_pathat()` wraps DFS path reads.

## Control Flow
The module delegates to the next `read_dfs_pathat` first. Null referral outputs mean check-only mode and return unchanged. Otherwise each referral `alternate_path` containing `@` is expanded in place; expansion failure frees the referral list and returns `NT_STATUS_NO_MEMORY`.

## State And Persistence
No private state is kept. Map files are read on demand. Substitution uses current connection/session attributes.

## Dependencies And Integration Points
The module uses MSDFS referral structures, tsocket remote address helpers, Samba substitution, loadparm substitution state, and lower DFS VFS hooks.

## Risks
Prefix matching is string-based and first-match. The parser requires a space delimiter. Map file paths come from DFS link content, so write access to links is sensitive. Lookup misses are reported as no-memory style failures. The parser mutates the target string while expanding.

## Test Signals
Test ordered prefix matching, default entries, malformed lines, missing files, substitution variables, referrals without `@`, check-only calls, IPv4/IPv6 address strings, and multiple referrals.
