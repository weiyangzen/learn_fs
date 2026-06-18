# sources/security-integrity/audit-userspace/auparse/auparse.pc.in

Purpose: pkg-config template for installed libauparse metadata.

Important APIs, types, and functions: Defines `prefix`, `exec_prefix`, `libdir`, and `includedir` substitutions. Exposes package `Name: libauparse`, description, `Version: @VERSION@`, `Libs: -L${libdir} -lauparse`, `Libs.private: -laudit`, and `Cflags: -I${includedir}`.

Control flow: No executable control flow. Configure substitutes variables and `auparse/Makefile.am` installs the generated `auparse.pc`.

State and persistence: Persistent installed metadata used by downstream builds.

Dependencies and integration points: Integrates libauparse with pkg-config consumers and records the private libaudit dependency for static linking.

Risks and edge cases: Incorrect `Libs.private` or include path can break downstream static or cross builds. Version substitution must match the release version.

Test signals: `pkg-config --cflags --libs auparse` in an installed or staged environment verifies the generated file.
