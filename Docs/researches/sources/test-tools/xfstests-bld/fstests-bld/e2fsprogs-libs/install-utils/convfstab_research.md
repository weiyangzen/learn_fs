<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/install-utils/convfstab -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/install-utils/convfstab

## Purpose
This legacy shell script rewrites `/etc/fstab` into a form with six fields by adding default mount options, dump frequency, and fsck pass numbers where they are missing.

## Important APIs, Types, and Functions
The script uses shell variables `ROOT_PASS`, `NON_ROOT_PASS`, `DEF_FLAGS`, and `DEF_DUMP`, reads `/etc/fstab` line by line, uses positional parameters via `set -- $LINE`, and writes transformed output to `/tmp/newfstab.$$`. It then renames `/etc/fstab` to `/etc/fstab.bak` and moves the temporary file into place.

## Control Flow
Blank lines are omitted with a warning. Lines starting with `#` or `!` are echoed back with warnings even though comments are described as non-standard. For non-comment entries, the script rejects lines with fewer than three or more than six fields. It sets pass `1` for root, `0` for `none`, `2` otherwise, then overrides dump/pass to zero for ignored, CD-ROM, DOS, network, proc, and swap-like filesystems. Depending on whether the line has three, four, five, or six fields, it appends the missing trailing fields.

## State and Persistence
This script directly mutates host state: it overwrites `/etc/fstab`, backs up the previous file to `/etc/fstab.bak`, and uses a PID-suffixed temporary file in `/tmp`.

## Dependencies and Integration Points
It depends on `/bin/sh`, root permissions, `/etc/fstab`, `/tmp`, and `mv`. It is an install utility rather than build-time code, and it assumes whitespace-delimited fstab fields without escaped spaces.

## Risks
This is high risk because it rewrites a critical boot configuration file in place, does not preserve ownership/mode explicitly, does not use atomic rename with validation, and can mishandle comments, escaped spaces, labels with spaces, or modern fstab conventions. A failed second `mv` after backing up `/etc/fstab` can leave no active fstab. The temp path is predictable modulo PID.

## Test Signals
Only test against temporary fixture files or a chroot/container. Useful fixtures include root, swap, proc, network, comments, blank lines, malformed entries, and already-six-field lines. Verify output fields, warnings, backup behavior, and failure handling when the destination cannot be replaced.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/install-utils/convfstab -->
