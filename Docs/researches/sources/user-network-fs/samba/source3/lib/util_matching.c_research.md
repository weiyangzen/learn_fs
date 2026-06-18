<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_matching.c -->
# sources/user-network-fs/samba/source3/lib/util_matching.c

## Purpose
`util_matching.c` builds reusable path-last-component matchers from slash-separated name lists, supporting Samba Microsoft wildcard matching or POSIX regex matching with one capture group.

## Important APIs, types, and functions
Opaque `struct samba_path_matching` contains case sensitivity, a matching function pointer, entry count, and entries. Entries store name, wildcard flag, or compiled regex. Public constructors are `samba_path_matching_mswild_create` and `samba_path_matching_regex_sub1_create`; matcher API is `samba_path_matching_check_last_component`.

## Control flow
`samba_path_matching_split` performs two passes over a slash-separated list, ignoring empty components, to allocate and copy entries. The mswild constructor marks entries containing Microsoft wildcard characters and uses `mask_match` or string comparison. The regex constructor compiles every entry and requires exactly one subexpression; it installs a destructor to `regfree` compiled patterns. The check function extracts the last path component, scans entries in order, and returns the first match index plus replacement offsets for regex capture group 1.

## State and persistence behavior
Matchers are talloc-owned and persist until freed. Regex resources are released by the talloc destructor. No external state is persisted.

## Dependencies and integration points
It depends on Samba path/string wrappers, `mask_match`, `ms_has_wild`, POSIX regex, NTSTATUS, and talloc. It is useful for VFS rules that match or rewrite filename components.

## Risks and edge cases
Regex mode rejects patterns with zero or more than one capture group. Replacement offsets are relative to the whole input name, not just the last component. Empty name lists create a valid matcher with no entries and no match. Constructor cleanup must avoid leaking partially compiled regexes.

## Test signals
Tests should cover repeated slashes, empty lists, case-sensitive and insensitive mswild matches, regex capture offset calculation, invalid regexes, invalid capture counts, and first-match ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_matching.c -->
