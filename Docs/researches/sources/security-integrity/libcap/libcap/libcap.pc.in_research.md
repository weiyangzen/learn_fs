## sources/security-integrity/libcap/libcap/libcap.pc.in

Purpose: pkg-config template for installed libcap.

Important fields: `prefix`, `exec_prefix`, `libdir`, `includedir`, `Name`, `Description`, `Version`, `Libs`, `Libs.private`, and `Cflags`.

Control flow: `libcap/Makefile` substitutes install paths, version, and private deps using sed to create `libcap.pc`.

State/persistence: template only; generated `.pc` file is installed.

Dependencies/integration: pkg-config consumers, Makefile substitution variables.

Risks: incorrect `Libs.private` or include path breaks static consumers; version substitution must match library soname release.

Test signals: `pkg-config --cflags --libs libcap` and static-link consumer build from staged install.
