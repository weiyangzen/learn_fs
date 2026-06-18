# File Research: sources/local-fs/gfs2-utils/gfs2/man/Makefile.am

Automake fragment for installing GFS2 man pages.

Behavior:
- Sets `MAINTAINERCLEANFILES = Makefile.in`.
- Installs man pages for fsck, filesystem format, edit, grow, jadd, mkfs, tune, lockcapture, trace, and glocktop.

Risk notes:
- Build/distribution-only file.
- Missing entries here would omit man pages from distribution/install.
