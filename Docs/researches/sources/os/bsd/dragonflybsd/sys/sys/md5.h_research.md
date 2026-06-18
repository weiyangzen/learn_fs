# File Research: sources/os/bsd/dragonflybsd/sys/sys/md5.h

Kernel-only MD5 interface and libmd/OpenSSL compatibility shim. Defines MD5 block/digest constants, `MD5_CTX`, and `MD5Init`, `MD5Update`, `MD5Final`.

Potential filesystem relevance through checksumming, protocol authentication, or compatibility code, though this header itself only declares the digest API.
