# sources/test-tools/xfstests-bld/fstests-bld/popt/popt.pc.in

Purpose: pkg-config template for installed popt consumers. It records install prefixes, library path, include path, package name, version, description, link flags, and C preprocessor include flags.

Important fields: `prefix`, `exec_prefix`, `libdir`, `includedir`, `Name`, `Version`, `Description`, `Libs`, and `Cflags`. `@VERSION@`, `@POPT_PKGCONFIG_LIBS@`, and directory variables are substituted by the build system.

Control flow/state: no runtime control flow. The generated `popt.pc` is persistent install metadata used by `pkg-config --libs popt` and `pkg-config --cflags popt`.

Dependencies/integration: integrates autotools/configure substitution with downstream build systems. `Libs` is intentionally template-driven so platform-specific library requirements can be injected.

Risks: incorrect substitution of `libdir`, `includedir`, or `POPT_PKGCONFIG_LIBS` breaks consumers at compile/link time. The file does not include `Requires`, so transitive dependencies must be encoded in `Libs` if needed.

Test signals: package installation tests or downstream compile tests should validate that generated `popt.pc` points to installed `popt.h` and libpopt.
