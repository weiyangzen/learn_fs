# File Research: sources/os/bsd/netbsd-src/lib/libradius/Makefile

This Makefile builds the NetBSD `libradius` network protocol library. It enables fortified-source behavior with `USE_FORT?= yes`, installs the shared library under the normal shared-library directory, sets warnings to level 3, and suppresses one lint warning class with `LINTFLAGS+= -Sw`.

It builds from `radlib.c`, installs `radlib.h` and `radlib_vs.h` into `/usr/include`, and installs manual pages `libradius.3` and `radius.conf.5`. The library is compiled with `-DWITH_SSL` and `-DOPENSSL_API_COMPAT=0x10100000L`, and links against OpenSSL libcrypto from the external crypto subtree. This enables HMAC/MD5 message authenticator support.
