# sources/security-integrity/selinux/libsepol/src/Makefile

Purpose: Builds and installs static/shared libsepol libraries, pkg-config metadata, symbol map, and optional CIL objects.

Important APIs and targets: Builds `libsepol.a`, `libsepol.so`/Darwin dylib, `libsepol.pc`, and `libsepol.map`; supports `DISABLE_CIL`, `DISABLE_SHARED`, `relabel`, and `clean`.

Control flow: Object lists are generated from local `.c` files and optionally CIL sources plus generated lexer. It probes for `reallocarray`, generates lexer via `flex`, compiles `.o`/`.lo`, links shared library with version script/soname, installs static/shared/pkgconfig artifacts, and creates relative symlink.

State and persistence: Produces build artifacts in `src/` and installs under `$(DESTDIR)$(LIBDIR)`/`$(SHLIBDIR)`.

Dependencies and integration points: Consumed by top-level builds and downstream packaging; ties CIL sources into libsepol unless disabled.

Risks: Wildcard object inclusion can pull unintended files. Darwin branch changes linker flags and symlink tool. Version map filtering when CIL disabled affects ABI exports.

Test signals: Static/shared builds with and without CIL/shared, install DESTDIR, pkg-config content, and clean target validate it.
