<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_path.h -->
# sources/user-network-fs/samba/source3/lib/util_path.h

## Purpose
This header declares source3 path utilities and the Windows previous-version timestamp format constants.

## Important APIs, types, and functions
It defines `GMT_NAME_LEN` and `GMT_FORMAT`, then declares `lock_path`, `state_path`, `cache_path`, `canonicalize_absolute_path`, snapshot-token helpers, `clistr_is_previous_version_path`, `subdir_of`, and `path_to_strv`.

## Control flow
Consumers call these functions for configured directory path construction, path normalization, previous-version parsing, and slash-list splitting.

## State and persistence behavior
The header has no state. Implementations may create configured directories or mutate token-containing path strings.

## Dependencies and integration points
It includes talloc and Samba time types, and is shared by VFS, configuration, and matching utilities.

## Risks and edge cases
Callers must pass mutable strings to extraction functions and absolute paths to `subdir_of`.

## Test signals
Compile coverage plus behavioral tests in `util_path.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_path.h -->
