# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/Makefile.am

## Purpose
Builds the `fsck.gfs2` filesystem checker.

## Main Elements
- Installs `fsck.gfs2` under `sbin_PROGRAMS`.
- Headers include pass helpers, hash/link/lost+found/metawalk/util/recovery declarations.
- Sources include block list, recovery, initialize, inode/link/lost+found, metawalk, passes 1-5, pass1b, rgrepair, and utilities.
- Links against `libgfs2`, gettext, and uuid.
- Includes `checks.am` when Check is available.

## Dependencies And Integration
Builds the full repair executable around libgfs2 and configured gettext/uuid support.

## Risk Notes
Unit test target reuses production fsck sources with compile-time suppressions, but the local test file is only a stub.
