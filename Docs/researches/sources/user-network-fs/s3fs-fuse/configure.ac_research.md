<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/configure.ac -->
# sources/user-network-fs/s3fs-fuse/configure.ac

Purpose: Autoconf source for configuring s3fs-fuse build dependencies, compiler flags, crypto backend selection, feature probes, generated files, manpage date, and commit hash macro.

Important APIs and macros: Initializes package `s3fs` version `1.97`, `config.h`, canonical host, automake, C/C++ compilers, and C++14 via `CPP_VERSION`. Probes xattr headers, `fallocate`, `malloc_trim`, `clock_gettime`, pthread recursive mutex symbol, libcurl options, and `dlopen`. Requires FUSE3 with platform-specific minimum versions. Supports `--with-openssl`, `--with-gnutls`, `--with-nettle`, and `--with-nss` with automake conditionals `USE_SSL_OPENSSL`, `USE_SSL_GNUTLS`, `USE_GNUTLS_NETTLE`, and `USE_SSL_NSS`.

Control flow: Sets hardening/portability CXXFLAGS (`-Wall`, no exceptions, file offset bits, `_FORTIFY_SOURCE`, C++14), selects min FUSE version by host, checks selected crypto backend dependencies via pkg-config and library probes, defines feature macros, substitutes `MAN_PAGE_DATE`, configures Makefiles and `doc/man/s3fs.1`, computes `COMMIT_HASH_VAL` from git or `default_commit_hash`, and runs `AC_OUTPUT`.

State and persistence: Generates `config.h`, Makefiles, manpage, and preprocessor definitions. The commit hash embeds dirty-state information using `git status -s --untracked-files=no`; despite the string text saying `+untracked files`, it actually reports tracked modifications.

Dependencies and integration points: Drives `src/Makefile.am` source selection for crypto backends and `doc/man/s3fs.1.in` substitution. It must align with CI package installation and source code `#ifdef`s for curl/FUSE/SSL features.

Risks: Crypto backend options are mutually constrained; invalid combinations fail configure. `_FORTIFY_SOURCE` detection compiles manually and depends on compiler warning text. Future OpenSSL/FUSE/pkg-config naming changes can break checks. The commit dirty label is misleading because untracked files are excluded.

Test signals: Run configure with default OpenSSL, explicit `--with-openssl`, `--with-gnutls`, `--with-nettle --with-gnutls`, and `--with-nss` where dependencies exist. CI matrix plus macOS build validates platform-specific FUSE minimum logic and feature probes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/configure.ac -->
