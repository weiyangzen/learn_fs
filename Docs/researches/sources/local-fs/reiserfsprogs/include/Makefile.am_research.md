# File Research: sources/local-fs/reiserfsprogs/include/Makefile.am

Autotools install manifest for public and private headers. It keeps `parse_time.h` and `progbar.h` as `noinst_HEADERS`, while installing `io.h`, `misc.h`, `reiserfs_fs.h`, `reiserfs_lib.h`, and `swab.h` under `$(includedir)/reiserfs`.
