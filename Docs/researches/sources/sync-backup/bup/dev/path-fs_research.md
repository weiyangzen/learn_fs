# sources/sync-backup/bup/dev/path-fs

## Purpose
Prints filesystem type for each supplied path in a platform-aware way.

## Important APIs, Types, and Functions
Uses `uname -s`, `df -G` on NetBSD, `df -g` on SunOS, and `df -T` with awk elsewhere.

## Control Flow
Defines an `fs` function based on kernel and loops over arguments printing one filesystem type per path.

## State and Persistence Behavior
Read-only system query.

## Dependencies and Integration Points
Used by `dev/lib.sh` and sparse-size fallback behavior.

## Risks and Test Signals
Risks are platform-specific `df` output changes and paths with unusual names. Signal is one filesystem type line per input.
