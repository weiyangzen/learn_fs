# sources/security-integrity/selinux/libsemanage/src/libsemanage.pc.in

Purpose: pkg-config template for consumers linking against libsemanage.

Important fields: defines `prefix`, `exec_prefix`, `libdir`, `includedir`, `Name`, `Description`, `Version`, project `URL`, `Requires.private` on `libselinux libsepol`, public `Libs: -L${libdir} -lsemanage`, private libraries `-laudit -lbz2`, and public include flags.

Control flow/build integration: configure/build tooling substitutes `@prefix@`, `@libdir@`, `@includedir@`, and `@VERSION@` to produce `libsemanage.pc`. Build systems use it for compiler/linker discovery.

State/persistence: no runtime state. The file affects installed metadata and downstream builds. Risks include missing private dependencies for static linking or incorrect substitution paths. Test signals are `pkg-config --cflags --libs libsemanage`, static link checks requiring private libs, and installed version consistency.
