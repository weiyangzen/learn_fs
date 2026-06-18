# File Research: sources/local-fs/ocfs2-tools/include/Makefile

This Makefile coordinates installation/distribution of public include subdirectories.

Key content:
- Includes top-level make preamble/postamble.
- Defines `SUBDIRS = tools-internal ocfs2-kernel o2dlm o2cb ocfs2`.

Integration notes:
- This is a routing Makefile; actual header lists live in child directories.
