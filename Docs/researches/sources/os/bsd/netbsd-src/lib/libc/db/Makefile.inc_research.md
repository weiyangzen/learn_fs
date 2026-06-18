# File Research: sources/os/bsd/netbsd-src/lib/libc/db/Makefile.inc

Read completely: 11 lines.

This makefile fragment enables private DB interfaces with `-D__DBINTERFACE_PRIVATE` and includes btree, db, hash, man, mpool, and recno subdirectory makefiles.

Security/reliability notes: build orchestration only; the private-interface define affects which DB internals are exposed during libc build.
