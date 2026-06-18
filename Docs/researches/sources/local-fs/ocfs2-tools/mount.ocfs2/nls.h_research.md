# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/nls.h

No-op native language support shim.

It undefines and replaces `bindtextdomain()` and `textdomain()` with empty macros and maps `_()`/`N_()` directly to their input strings. This lets util-linux-derived code keep translatable-message syntax without linking an actual NLS layer here.
