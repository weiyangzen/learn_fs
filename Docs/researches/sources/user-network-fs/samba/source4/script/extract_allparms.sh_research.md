<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/extract_allparms.sh -->
# sources/user-network-fs/samba/source4/script/extract_allparms.sh

## Purpose

This shell helper extracts Samba loadparm option names and whether they are local or global from `param/loadparm.c`.

## Important APIs, Types, and Functions

It uses a single `grep` pipeline with `sed` transformations and `sort -f`. It searches for table entries matching `{"...P_[GL]`.

## Control Flow

The script reads `param/loadparm.c`, strips trailing initializer content, maps `P_LOCAL` entries to `S`, maps `P_GLOBAL` entries to `G`, removes leading syntax, and sorts case-insensitively.

## State and Persistence Behavior

It writes only to stdout and has no persistent state.

## Dependencies and Integration Points

It depends on POSIX shell, `grep`, `sed`, and `sort`, and assumes it is run from a source tree where `param/loadparm.c` is present.

## Risks and Edge Cases

The parsing is brittle and tied to the C initializer formatting in `loadparm.c`. It does not handle unusual whitespace or multiline entries outside the expected pattern.

## Test Signals

Tests should compare output against representative `loadparm.c` snippets containing local, global, mixed-case, and unusual spacing entries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/extract_allparms.sh -->
