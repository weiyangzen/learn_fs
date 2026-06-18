# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/mount.ocfs2.h

Shared include header for the OCFS2 mount helper.

It enables large-file/GNU interfaces, pulls in system mount, path, option, mtab, allocation, and libocfs2 headers, and supplies fallback `MS_*` mount flag definitions for older build environments. It centralizes the local helper dependencies used by `mount.ocfs2.c` and `opts.c`.
