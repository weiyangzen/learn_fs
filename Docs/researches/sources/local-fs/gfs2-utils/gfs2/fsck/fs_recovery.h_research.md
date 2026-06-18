# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/fs_recovery.h

## Purpose
Declares journal recovery and journal-index helpers for `fsck.gfs2`.

## Main Elements
- `replay_journals()`.
- `preen_is_safe()`.
- `ji_update()`.
- `build_jindex()`.
- `init_jindex()`.

## Dependencies And Integration
Includes `libgfs2.h` for `fsck_cx`, `lgfs2_sbd`, and option-related types.

## Risk Notes
Functions include both read-only validation and mutating recovery/rebuild operations; callers must honor options and safety checks.
