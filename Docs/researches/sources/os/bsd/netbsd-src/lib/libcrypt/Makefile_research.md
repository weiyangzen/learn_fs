# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/Makefile

Read completely: 54 lines.

Builds NetBSD `libcrypt`. Core sources are DES/dispatcher `crypt.c`, `md5crypt.c`, `bcrypt.c`, `crypt-sha1.c`, `util.c`, `pw_gensalt.c`, and `hmac_sha1.c`. The build force-includes `namespace.h` to hide imported Argon2 and helper symbols.

When `MKARGON2` is enabled, it defines `HAVE_ARGON2`, adds `crypt-argon2.c`, imports Argon2 upstream source files from `external/apache2/argon2`, disables Argon2 threads with `ARGON2_NO_THREADS`, and marks imported sources hidden. The Makefile installs `crypt.3` and `pw_gensalt.3` manuals and exposes `encrypt`/`setkey` manual links.

It also carries a compiler workaround for `crypt.c` stringop-overflow warnings around DES permutation table initialization and supports unit-test builds through a `.c.test` suffix rule.
