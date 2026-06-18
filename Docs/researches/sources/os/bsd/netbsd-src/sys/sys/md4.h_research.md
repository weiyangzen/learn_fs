# File Research: sources/os/bsd/netbsd-src/sys/sys/md4.h

Declares the MD4 digest context and API. It defines digest/string/block lengths, `MD4_CTX`, and init/update/final functions, with userland convenience helpers for ending, hashing files, and hashing data omitted in kernel builds.

This is a legacy cryptographic hash interface. Risks are security misuse: MD4 is obsolete for collision-resistant purposes and should only be used for compatibility protocols requiring MD4.
