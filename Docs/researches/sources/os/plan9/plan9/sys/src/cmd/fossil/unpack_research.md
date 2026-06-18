# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/unpack

This is an `rc` script for unpacking a Plan 9 distribution ISO into `/n/ehime/testplan9`. It copies and decompresses `plan9.iso.bz2`, starts `9660srv`, mounts the ISO, recreates the destination tree, runs `dircp`, and creates an extra `/n/emelieother` directory for `lp`.

It is operational/test data movement glue, not C source.
