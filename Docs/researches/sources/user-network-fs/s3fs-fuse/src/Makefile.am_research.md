<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/Makefile.am -->
# sources/user-network-fs/s3fs-fuse/src/Makefile.am

Purpose: Automake file defining the main `s3fs` binary, crypto-backend source selection, unit test helper binaries, and clang-tidy target for the source directory.

Important fields: `bin_PROGRAMS=s3fs`; `AM_CPPFLAGS=$(DEPS_CFLAGS)` plus `-DUSE_GNUTLS_NETTLE` when applicable; conditional `AUTH_SOURCES` selects `openssl_auth.cpp`, `gnutls_auth.cpp`, or `nss_auth.cpp`. `s3fs_SOURCES` includes core filesystem, curl, cache, credential, fd-cache, threading, metadata, additional-header, signal, and sync filler modules. `noinst_PROGRAMS` defines `test_curl_util`, `test_page_list`, and `test_string_util`; `TESTS` runs them.

Control flow and integration: `configure.ac` conditionals determine authentication source composition and `DEPS_*` flags/libs. `make check -C src` builds and runs the unit helper programs. `clang-tidy` runs over headers, main sources, and test sources with configured C++ standard and dependency flags.

State and persistence: No runtime state. Determines which object files are built and linked into `s3fs` and tests.

Dependencies and risks: Source list must stay in sync with new modules; missing additions cause build/link failures or omitted functionality. Conditional auth source logic must match configure backend choices. The clang-tidy target uses shell globbing and broad source lists, so new files may need explicit inclusion.

Test signals: `make -C src`, `make check -C src`, and `make -C src clang-tidy` validate build composition and unit binaries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/Makefile.am -->
