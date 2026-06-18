# File Research: sources/local-fs/gfs2-utils/gfs2/tune/Makefile.am

Automake definition for the `tunegfs2` utility.

Builds:
- `sbin_PROGRAMS = tunegfs2`
- Sources: `main.c`, `super.c`
- Header: `tunegfs2.h`

Links:
- `gfs2/libgfs2/libgfs2.la`
- `$(LTLIBINTL)`
- `$(uuid_LIBS)`

Conditional:
- Includes `checks.am` when `HAVE_CHECK` is true.

Research notes:
- The tune utility is smaller than mkfs and primarily edits/list superblock fields.
