# File Research: sources/virtualization/nbdkit/filters/luks/Makefile.am

Automake rules for `nbdkit-luks-filter.la`, gated by `HAVE_GNUTLS_PBKDF2`. Builds `luks.c`, `luks-encryption.c`, and `luks-encryption.h`.

Uses nbdkit/common include paths, common utils, compatibility replacements, GnuTLS CFLAGS/libs, Windows import hook, module/shared flags, and optional filter linker script. POD man page generation is conditional.
