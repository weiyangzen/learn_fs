# sources/security-integrity/selinux/libsepol/src/libsepol.pc.in

Purpose: pkg-config template for libsepol consumers. It describes include and library flags needed to compile and link software against libsepol.

Important fields: `prefix`, `exec_prefix`, `libdir`, and `includedir` are substituted by the build/install system. `Name`, `Description`, `Version`, and `URL` identify the package. `Libs: -L${libdir} -lsepol` supplies linker flags, and `Cflags: -I${includedir}` supplies include flags.

Control flow: no runtime control flow. The template becomes `libsepol.pc` at install/configure time and is read by `pkg-config`.

State and persistence: persists as installed metadata. Incorrect substituted paths or version values affect all downstream builds using `pkg-config --cflags --libs libsepol`.

Dependencies and integration points: depends on build-system substitution for `@prefix@`, `@libdir@`, `@includedir@`, and `@VERSION@`. Used by package managers and external SELinux consumers.

Risks: stale version or install directories can make consumers build against the wrong headers or fail to find the library. The file intentionally does not list private libs; if libsepol gains additional public link dependencies, this template may need updates.

Test signals: after installation, run `pkg-config --modversion libsepol`, `pkg-config --cflags --libs libsepol`, and compile a minimal program including a public libsepol header and linking with the returned flags.
