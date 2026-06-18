# sources/sync-backup/git-crypt/Makefile

Purpose: simple portable Makefile for building, optionally generating the manpage, cleaning, and installing the git-crypt binary and manpage.

Important APIs/types/functions: variables `CXXFLAGS`, `PREFIX`, `BINDIR`, `MANDIR`, `ENABLE_MAN`, `DOCBOOK_XSL`, `OBJFILES`, `LDFLAGS`, `XSLTPROC`, and `DOCBOOK_FLAGS`; targets `all`, `build`, `build-bin`, `git-crypt`, `build-man`, `clean`, `install`, and related `*-bin`/`*-man` targets.

Control flow: default `all` maps to `build`. `BUILD_TARGETS` conditionally includes `build-man` based on `ENABLE_MAN`. `git-crypt` links C++11 objects against `-lcrypto`. `util.o` and `coprocess.o` depend on both platform-specific implementation files because their `.cpp` files include the selected platform source. Manpage generation runs `xsltproc` over `man/git-crypt.xml`.

State/persistence behavior: build outputs are object files, `git-crypt`, and optionally `man/man1/git-crypt.1`. Install creates destination directories under `DESTDIR` plus prefix paths and copies the binary/manpage with expected modes.

Dependencies/integration: requires a C++11 compiler, OpenSSL libcrypto, make, and optionally `xsltproc` plus DocBook XSL. Release workflows invoke `make` directly and override `LDFLAGS` for Windows.

Risks/test signals: no dependency auto-generation for headers; platform-specific source inclusion is unusual but intentional. Test signals are clean rebuilds on Linux and Windows, optional `ENABLE_MAN=yes`, `make install DESTDIR=...`, and link failures against newer OpenSSL.
