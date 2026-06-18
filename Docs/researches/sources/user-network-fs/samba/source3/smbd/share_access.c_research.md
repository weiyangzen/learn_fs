# sources/user-network-fs/samba/source3/smbd/share_access.c

## Purpose

`share_access.c` evaluates share-level access rules against a user's security token. It implements membership checks for `invalid users`, `valid users`, `read list`, and `write list`, using expanded names and SID-based token comparisons rather than trusting text names directly.

## Important APIs, Types, And Functions

- `token_contains_name_in_list()` iterates a NULL-terminated list of configured names/groups, expands/evaluates each through `token_contains_name()`, and reports whether any entry matches the token.
- `user_ok_token()` denies users listed in `invalid users`, requires membership in `valid users` when configured, and otherwise permits access.
- `is_share_read_only_for_token()` starts from `conn->read_only`, forces read-only on `read list` match, and allows write on `write list` match.

Inputs include username, domain, share name/service number, `struct security_token`, loadparm list values, and connection state.

## Control Flow

The shared helper starts with `*match = false`, treats a NULL list as success/no match, and for each entry creates a stackframe, calls `token_contains_name()` with username/domain/share/token/list entry, frees the frame, returns false on lookup/evaluation failure, returns true immediately on match, and otherwise continues.

`user_ok_token()` first checks `invalid users`; a match denies immediately. It then checks `valid users`; if configured and no match is found, access is denied. `is_share_read_only_for_token()` checks `read list` first and sets `read_only = true` on match, then checks `write list` and sets `read_only = false` on match, so `write list` can override a prior read-list match.

## State And Persistence Behavior

No persistent state is written. The functions read live loadparm share parameters and connection state and return decisions through booleans or `_read_only`. Temporary talloc stackframes isolate substitution/lookup allocations for each list entry. The final read-only decision is not stored here; the caller must apply it to connection/session behavior.

## Dependencies And Integration Points

This file depends on loadparm share accessors, loadparm global substitution context, `token_contains_name()`, security tokens, `connection_struct`, and debug logging. It integrates with tree connect/share access setup and with later file-open decisions through the share read-only result.

## Risks

Access decisions rely on SID comparisons after name lookup, which is safer than text comparison but sensitive to lookup failures. The helper returns false on lookup error, and callers treat that as denial. List ordering is simple OR matching; there is no negative entry precedence inside a single list. `write list` overriding `read list` is an intentional semantic that tests should preserve. Repeated `lp_servicename(talloc_tos(), ...)` calls depend on the surrounding talloc stack behavior.

## Test Signals

Tests should cover NULL lists, direct user entries, domain-qualified names, group/netgroup entries, lookup failure denial, `invalid users` precedence over `valid users`, configured `valid users` requiring membership, `read list` forcing read-only, `write list` overriding read-only, and substituted share/user names in list entries.
