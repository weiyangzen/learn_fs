# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/metafs.h

Header for the metafs helper API.

Defines:
- `extern int metafs_interrupted`
- `struct metafs { int fd; char *path; char *context; }`

Exports:
- `mount_gfs2_meta`
- `cleanup_metafs`
- `copy_context_opt`

Research notes:
- `context` is documented as the SELinux-style `context=` mount option and is passed through to the `gfs2meta` mount.
