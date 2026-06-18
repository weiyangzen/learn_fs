# File Research: sources/os/bsd/netbsd-src/sys/sys/md5.h

Declares the MD5 digest context and API. It defines digest/string/block lengths, `MD5_CTX`, init/update/final routines, and userland convenience functions for string, file, and memory hashing.

Like MD4, this is a compatibility hash interface rather than a modern security primitive. Risks are misuse for integrity/security decisions requiring collision resistance.
