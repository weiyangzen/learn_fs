# File Research: sources/os/plan9/9front/sys/src/cmd/git/util.c

Shared utility layer for the 9front git implementation. It installs hash/type/object/Qid formatters, initializes zlib and regex parsing, locates repository roots, parses SHA-1 strings and Qids, validates ref names, provides checked allocation helpers, string helpers, directory reading, progress display, and MurmurHash2 for pack delta grouping.

It also defines `emptydir`, git tree entry ordering compatible with git's directory-sorts-as-trailing-slash rule, and `Objq`, a max-heap by commit time used for commit graph traversals.
