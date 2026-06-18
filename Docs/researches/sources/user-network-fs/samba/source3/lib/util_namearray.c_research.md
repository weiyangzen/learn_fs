<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_namearray.c -->
# sources/user-network-fs/samba/source3/lib/util_namearray.c

## Purpose
`util_namearray.c` parses slash-separated name lists into `name_compare_entry` arrays and checks whether security tokens contain users/groups/netgroups named by configured expressions.

## Important APIs, types, and functions
Public functions include `token_contains_name`, `append_to_namearray`, and `set_namearray`. Internal `do_group_checks` interprets name prefixes: direct user, `@` netgroup then Unix group, `&` netgroup, `+` Unix/domain group, and combined `+&`/`&+` order. `namearray_len` finds the terminator.

## Control flow
`token_contains_name` applies user/domain/share substitutions, recognizes literal SID strings, resolves direct names through `lookup_name_smbconf_ex`, validates expected SID type, and checks token SIDs. Group-prefixed names iterate requested lookup modes: `+` resolves groups and checks token SID membership; `&` calls `user_in_netgroup`. Name-array parsing converts `/` to string-vector separators via `path_to_strv`, skips empty components, appends entries, and precomputes `is_wild` using `ms_has_wild`.

## State and persistence behavior
Functions allocate talloc-owned arrays and substituted strings. No persistent state is modified.

## Dependencies and integration points
It depends on loadparm winbind separator, talloc substitution helpers, passdb/name lookup, netgroup checks, security tokens, SID type utilities, `path_to_strv`, and wildcard helpers. It feeds share access and path include/exclude style checks.

## Risks and edge cases
Name substitutions can fail allocation. Direct names that resolve to non-user SID types return success with no match but log a warning. Group lookup failures return false, distinguishing lookup error from no match. Prefix ordering matters for combined netgroup/group syntax.

## Test signals
Tests should cover all prefixes, domain stripping from usernames, `%S` substitution, direct SID matching, non-user/non-group type warnings, repeated slash parsing, wildcard flag precomputation, and append versus reset behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_namearray.c -->
