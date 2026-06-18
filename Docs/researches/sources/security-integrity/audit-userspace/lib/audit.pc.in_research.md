# sources/security-integrity/audit-userspace/lib/audit.pc.in

Purpose: pkg-config template for applications linking against libaudit.

Important fields: Substitutes `prefix`, `exec_prefix`, `libdir`, `includedir`, `Version`, `Libs=-L${libdir} -laudit`, `Libs.private=@CAPNG_LDADD@`, `Cflags=-I${includedir}`, and `Requires.private=@CAPNG_PKG@`.

Control flow: Declarative template processed by configure into `audit.pc`.

State and persistence: Installed pkg-config metadata under `$(libdir)/pkgconfig`.

Dependencies and integration: Reflects libcap-ng private dependencies discovered by configure and consumed by downstream builds using `pkg-config --libs audit`.

Risks: Incorrect private deps break static linking. Incorrect include/lib paths break downstream builds.

Test signals: `pkg-config --cflags --libs audit`, `pkg-config --static --libs audit`, and downstream compile/link smoke tests.
