# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/trofftable/trofftable.mk

Purpose: Makefile for building/installing the `trofftable` shell script and related PostScript/manual assets.

Key behavior:
- Defines system/version, ownership/group, font/postscript install paths, and man-page directory.
- `trofftable` target rewrites path variables in `trofftable.sh` using `sed`.
- `install` creates target directories if absent, installs executable, `trofftable.ps`, and man page with ownership/mode.
- `clobber` removes generated script.
- `changes` rewrites makefile and manual defaults from current variables.

Dependencies and integration:
- Expects `trofftable.sh`, `trofftable.ps`, and `trofftable.1`.
- Uses traditional Unix `/bin/make`, `sed`, `cp`, `chmod`, `chgrp`, and `chown`.

Risks and notes:
- `clean` is empty.
- Install paths default to old Unix-style directories, not Plan 9 `/sys`.
