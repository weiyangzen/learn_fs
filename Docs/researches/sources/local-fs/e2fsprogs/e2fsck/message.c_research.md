# File Research: sources/local-fs/e2fsprogs/e2fsck/message.c

## Purpose
Formats e2fsck diagnostic/problem messages with abbreviation compression, pathname expansion, inode/dirent fields, safe string printing, and localization hooks.

## Expansion Types
Supports:
- `%` expressions for block numbers, inode numbers, groups, errors, paths, times, quotas, checksums, strings, backup superblock, and numeric formatting.
- `%I*` inode field expressions for size, blocks, links, mode, mtime, file ACL, UID/GID, type, etc.
- `%D*` directory entry expressions for inode, name, rec_len, name_len, and file type.
- `@` abbreviation expressions such as inode, block, filesystem, journal, directory, quota, extent, lost+found, and composite phrases.

## Main Behavior
- `safe_print()` escapes non-printable and high-bit characters.
- `print_pathname()` maps special inode numbers to friendly names or calls `ext2fs_get_pathname()`.
- `print_time()` formats local/GMT time.
- `expand_at_expression()` recursively expands abbreviations with recursion limit.
- `print_e2fsck_message()` walks a template, clears progress UI, and emits fully expanded text.

## Integration
Used by problem reporting (`problem.c`) and general diagnostics. It consumes `struct problem_context` fields.

## Risks / Notes
The template language is compact but highly coupled to `problem_context`; missing context values fall back to literal `%` expressions.
