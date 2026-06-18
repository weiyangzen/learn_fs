# File Research: sources/os/linux/linux/fs/gfs2/gfs2.h

## Scope

Small common GFS2 header defining simple shared constants used across the filesystem.

## APIs And Constants

- Defines `NO_CREATE` / `CREATE` for object lookup or allocation call sites.
- Defines `NO_FORCE` / `FORCE` for call sites with optional forced behavior.
- Defines `GFS2_FAST_NAME_SIZE` as `8`, used for small-name storage thresholds elsewhere in GFS2.

## Dependencies And Invariants

- Has no external includes beyond its include guard.
- Provides intentionally minimal shared constants; semantic meaning comes from the call sites using these flags.
