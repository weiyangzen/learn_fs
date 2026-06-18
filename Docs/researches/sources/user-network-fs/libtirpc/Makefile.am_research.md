<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/Makefile.am -->
# sources/user-network-fs/libtirpc/Makefile.am

Purpose: Top-level Automake file for libtirpc source, headers, pkg-config metadata, and subdirectories.

Important APIs, types, and functions: Defines `SUBDIRS = src man doc`, `ACLOCAL_AMFLAGS`, private `noinst_HEADERS`, installed `nobase_include_HEADERS`, conditional GSS headers, `pkgconfig_DATA`, and clean/distclean files.

Control flow: Automake recurses into subdirectories, installs public tirpc headers preserving paths, and installs `libtirpc.pc`.

State and persistence behavior: No runtime state; controls installed headers and generated build artifacts.

Dependencies and integration points: Driven by `configure.ac` conditionals, especially `GSS`. Integrates source, man, doc, and pkg-config outputs.

Risks: Header lists can drift from source. Conditional GSS headers must match library symbols and configure checks.

Test signals: Build/install success is the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/Makefile.am -->
