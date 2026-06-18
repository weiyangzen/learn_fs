# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tdb/build-tdb

Shell script used to rebuild the standalone bundled TDB files from a Samba checkout. It sets `BASE_DIR`, removes `.pc`, captures SVN metadata, starts a generated `tdb.c` with source URL/revision/date, appends `tdb_private.h`, and concatenates selected Samba common files after stripping includes up to `tdb_private.h`.

The source list includes error, lock, io, transaction, freelist, freelistcheck, traverse, dump, tdb, and open modules. It also copies `tdb.h` and `tdbtool.c`, then runs `quilt push -a`, implying local patch application after import.
