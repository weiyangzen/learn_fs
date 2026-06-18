# File Research: sources/os/bsd/netbsd-src/lib/libc/cdb/Makefile.inc

## Summary
Build fragment for libc constant database reader/writer support.

## Key Details
- Adds local `cdb` and common libc `cdb` directories to `.PATH`.
- Builds `cdbr.c` and `cdbw.c`.
- Installs manuals `cdbr.3`, `cdbw.3`, and `cdb.5`.
- Adds manual links for reader APIs such as `cdbr_open`, `cdbr_get`, and `cdbr_close`.
- Adds manual links for writer APIs such as `cdbw_open`, `cdbw_put`, `cdbw_output`, and `cdbw_close`.
- Adds lint suppressions for `cdbw.c` and disables `calloc` transposed-argument warnings for that file.

## Notes
The comment says the lint workaround should eventually be fixed in the code.
