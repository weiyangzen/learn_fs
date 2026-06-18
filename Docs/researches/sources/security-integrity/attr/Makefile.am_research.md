## sources/security-integrity/attr/Makefile.am

Purpose: top-level Automake aggregation for the attr project.

It sets include paths, locale/sysconf defines, pkg-config install location, initializes program/library/header/man/doc variables, installs `xattr.conf`, and includes all module fragments. State is build-system metadata only; persistence is generated Makefiles and installed artifacts. Dependencies are Automake, gettext `po`, libtool fragments, and module files. Risks are module-order coupling because fragments append to shared variables. Test signals are `autoreconf`, `make`, `make install`, and `make check`.
