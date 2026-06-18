# sources/security-integrity/selinux/libsemanage/src/Makefile

Purpose: builds libsemanage static/shared libraries, pkg-config metadata, generated lexer/parser sources, SWIG Python and Ruby bindings, and install artifacts.

Important APIs/targets: defines Python/Ruby discovery variables, install directories, `LIBA`, `LIBSO`, `LIBPC`, SWIG targets, generated files, `SRCS/OBJS/LOBJS`, compiler flags, `all`, `pywrap`, `rubywrap`, `install`, wrapper installs, `relabel`, `clean`, and `distclean`. It generates `conf-scan.c` with flex and `conf-parse.c/.h` with bison.

Control flow: normal builds compile all C sources except generated wrappers, compile parser/lexer with `-Werror` filtered out, archive `libsemanage.a`, link `libsemanage.so.2` against libsepol, libselinux, audit, and bzip2, then create the `libsemanage.so` symlink. Wrapper targets depend on the library and generated SWIG C.

State and persistence behavior: writes object files, PIC objects, generated parser/lexer/SWIG files, shared/static libraries, pkg-config file, and installed library/config/binding files under `DESTDIR`. `distclean` removes generated binding and parser products.

Dependencies and integration points: integrates C compiler, flex, bison, SWIG, pkg-config, Python sysconfig, Ruby RbConfig, libselinux, libsepol, libaudit, and bz2. The version script and soname define exported ABI.

Risks: toolchain discovery is host-sensitive, generated sources can become stale, parser warnings are intentionally tolerated, and `-z defs` catches unresolved symbols only in shared builds. Test signals are clean static/shared builds, wrapper imports, pkg-config metadata correctness, install staging, and ABI symbol-map checks.
