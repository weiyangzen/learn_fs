# File Research: sources/local-fs/reiserfsprogs/reiserfscore/Makefile.am

Builds and installs `libreiserfscore.la`. It generates `reiserfs_err.c` and `reiserfs_err.h` from `reiserfs_err.et` using `compile_et`, installs `reiserfs_err.h`, and compiles core sources including balancing, searching, hashing, printing, node formats, library logic, bitmap, journal, and xattr support. Links against `../lib/libmisc.la` and `-lcom_err`, and installs `reiserfscore.pc`.
