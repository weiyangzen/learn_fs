# File Research: sources/local-fs/gfs2-utils/gfs2/include/Makefile.am

This Automake fragment declares private headers for the GFS2 userspace build.

It marks `Makefile.in` as maintainer-clean and lists `noinst_HEADERS`:
- `osi_list.h`
- `osi_tree.h`
- `linux/gfs2_ondisk.h`
- `linux/types.h`
- `logging.h`

These headers are not installed as public system headers by this target; they are internal build inputs for the gfs2-utils source tree.
