<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_matching.h -->
# sources/user-network-fs/samba/source3/lib/util_matching.h

## Purpose
This header declares the opaque path matching API.

## Important APIs, types, and functions
It forward declares `struct samba_path_matching` and exposes constructors for Microsoft wildcard and regex-substitution modes plus `samba_path_matching_check_last_component`.

## Control flow
Callers create a matcher once from a name list, then call the check function for paths. Regex mode additionally returns capture replacement offsets.

## State and persistence behavior
The matcher object is allocated under caller-provided talloc memory and owns parsed entries and compiled regex state.

## Dependencies and integration points
It is included by code that wants a stable matching abstraction without knowing whether mswild or regex is used internally.

## Risks and edge cases
Callers must free the matcher to release regex resources and must handle `match_idx == -1` as no match, even when NTSTATUS is OK.

## Test signals
Compile coverage plus constructor and match behavior tests in `util_matching.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_matching.h -->
