# File Research: sources/os/bsd/netbsd-src/lib/libc/md/Makefile.inc

Read completely: 27 lines.

This makefile fragment adds MD4/MD5 libc sources and manual pages. It includes `md4c.c`, `md5c.c`, `md4hl.c`, and `md5hl.c`, registers man pages and links for init/update/final/end/file/data APIs, and generates `md4.3`/`md5.3` from `mdX.3` plus algorithm-specific copyright text.

Important interactions: `md4hl.c` and `md5hl.c` are generated-style instantiations of `mdXhl.c`.

Security/reliability notes: no runtime behavior. MD4 and MD5 are legacy hash algorithms and should not be treated as collision-resistant for new security uses.
