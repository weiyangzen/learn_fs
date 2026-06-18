<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/find_unused_options.sh -->
# sources/user-network-fs/samba/source4/script/find_unused_options.sh

## Purpose

`find_unused_options.sh` is a maintenance helper that identifies generated `lp_*()` loadparm accessor functions that appear unused in C files.

## Important APIs, Types, and Functions

It builds `LIST_GLOBAL` from `FN_GLOBAL` macros and `LIST_LOCAL` from `FN_LOCAL` macros in `param/loadparm.c`, scans all `*.c` files from the current directory, and reports accessors with no grep hits.

## Control Flow

For each global accessor, it searches for `key()` calls. For each local accessor, it searches for `key(` calls. Missing hits produce `Not Used Global` or `Not Used LOCAL` messages. A final reminder tells maintainers to clean and rebuild before removal.

## State and Persistence Behavior

The script reads source files and writes findings to stdout. It does not modify files.

## Dependencies and Integration Points

It depends on shell, `grep`, `sed`, `cut`, and `find`, and on `param/loadparm.c` macro formatting.

## Risks and Edge Cases

Plain grep can miss macro-indirect or generated uses and can produce false positives from comments or strings. Local and global search regexes differ, which may change sensitivity. It scans from the current directory and can include generated or irrelevant C files.

## Test Signals

Tests should use fixture `loadparm.c` and C files with direct calls, comment-only mentions, macro uses, and unused functions to characterize false positives/negatives.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/find_unused_options.sh -->
