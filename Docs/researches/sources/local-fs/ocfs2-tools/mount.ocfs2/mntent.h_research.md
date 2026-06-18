# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/mntent.h

Declares the private mount-entry API used by `mount.ocfs2`.

It defines `struct my_mntent`, the `mntFILE` wrapper around `FILE *` plus parse state, the soft-error limit `ERR_MAX`, and prototypes for opening, closing, appending, and reading mount table entries.
