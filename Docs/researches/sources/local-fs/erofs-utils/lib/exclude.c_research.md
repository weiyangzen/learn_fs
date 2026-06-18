# File Research: sources/local-fs/erofs-utils/lib/exclude.c

## Purpose
Maintains exact-path and regex-based exclude rules for mkfs/import source traversal.

## Main Data
- `exclude_head`: exact path rules.
- `regex_exclude_head`: compiled regex rules.

## Important Functions
- `erofs_parse_exclude_path()`: inserts an exact or regex exclude rule.
- `erofs_is_exclude_path()`: builds `dir/name`, converts to fs-relative path, and checks exact then regex rules.
- `erofs_cleanup_exclude_rules()`: frees patterns and regex resources.

## Behavior
- Regex rules compile with `REG_EXTENDED | REG_NOSUB`.
- Invalid regex errors are logged with `regerror()`.
- On insertion failure, all existing exclude rules are cleaned up.

## Interactions
- Uses `erofs_fspath()` from `config.c` for root-relative matching.

## Notes
`erofs_is_exclude_path()` uses a fixed `PATH_MAX` stack buffer for `dir/name`.
