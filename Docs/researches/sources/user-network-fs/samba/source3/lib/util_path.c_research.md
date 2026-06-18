<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_path.c -->
# sources/user-network-fs/samba/source3/lib/util_path.c

## Purpose
`util_path.c` builds configured Samba state/lock/cache paths, canonicalizes absolute POSIX paths, extracts Windows previous-version `@GMT-` snapshot tokens, tests parent/subdirectory relationships, and converts slash-separated paths to string vectors.

## Important APIs, types, and functions
Public APIs are `lock_path`, `state_path`, `cache_path`, `canonicalize_absolute_path`, `clistr_is_previous_version_path`, `extract_snapshot_token`, `clistr_smb2_extract_snapshot_token`, `subdir_of`, and `path_to_strv`. Internal helpers include `xx_path`, `find_snapshot_token`, and `extract_snapshot_token_internal`.

## Control flow
Path builders trim trailing slashes from configured root directories, ensure the directory exists with mode 0755, and append the requested name. Canonicalization always emits an absolute path, collapses duplicate slashes, removes `.` components, and handles `..` without escaping above root. Snapshot detection finds a path-component-starting `@GMT-%Y.%m.%d-%H.%M.%S` token, converts it via `timegm` to NTTIME, and optionally removes the component from the path. `subdir_of` compares normalized absolute strings and returns the relative suffix.

## State and persistence behavior
Path builders may create lock/state/cache directories. Other functions allocate or mutate caller-provided strings only.

## Dependencies and integration points
It depends on loadparm directories, `directory_create_or_exist`, Samba time conversion, string wrappers, and talloc. It is used by server file paths, shadow-copy/previous-version handling, and name-list parsing.

## Risks and edge cases
`canonicalize_absolute_path` treats any input as absolute by prepending `/`. Snapshot token parsing requires the token to be a complete path component and uses different separators for POSIX and SMB2 client paths. `subdir_of` assumes both inputs begin with `/` and asserts otherwise.

## Test signals
Tests should cover empty path canonicalization, root-preserving `..`, duplicate separators, invalid and valid `@GMT-` tokens, token removal, parent with trailing slash, root parent behavior, and path-to-strv empty components.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_path.c -->
