## sources/security-integrity/ecryptfs-utils/tests/lib/Makefile.am

Purpose: Automake fragment for shared eCryptfs test-library artifacts. It distributes `etl_funcs.sh` and builds the helper program `etl-add-passphrase-key-to-keyring`.

Important APIs and functions: `dist_noinst_SCRIPTS`, `noinst_PROGRAMS`, `_SOURCES`, and `_LDADD`. Control flow is build-system declarative: compile `etl_add_passphrase_key_to_keyring.c` and link it with `$(top_builddir)/src/libecryptfs/libecryptfs.la`.

State and persistence: Produces a non-installed test helper binary in the build tree; no runtime state. Dependencies are automake/libtool and libecryptfs. Integration is central: shell tests call `tests/lib/etl-add-passphrase-key-to-keyring` through `etl_funcs.sh` to populate the kernel keyring. Risks include build ordering/linkage failures breaking most kernel tests, because mount helpers depend on generated key signatures.
