# sources/user-network-fs/samba/source4/dsdb/samdb.pc.in

## Purpose
`samdb.pc.in` is the pkg-config template for the Samba SAM database client library. During configuration, build variables are substituted so external or internal consumers can discover the include path, library path, version, linker flags, and compiler flags needed to compile against `libsamdb`.

## Important fields
- `prefix`, `exec_prefix`, `libdir`, and `includedir` are configure-time installation path substitutions.
- `Name`, `Description`, and `Version` identify the package as `samdb` / "Sam Database" using `@PACKAGE_VERSION@`.
- `Libs` emits `@LIB_RPATH@ -L${libdir} -lsamdb`, so consumers link to `libsamdb` and receive any configured runtime path flags.
- `Cflags` emits `-I${includedir} -DHAVE_IMMEDIATE_STRUCTURES=1`; the define is part of the ABI/headers expectation for immediate structure support.

## Control flow
There is no executable control flow. The build system substitutes Autoconf/Waf-style variables into this template and installs or stages the resulting `samdb.pc` file.

## State and persistence behavior
The generated `.pc` file persists build/install metadata. It does not mutate runtime state, but stale or incorrect substitutions can affect every downstream compile/link invocation that relies on pkg-config.

## Dependencies and integration points
It integrates with the Samba build configuration, `pkg-config`, and consumers of `libsamdb`. The link line assumes the library is installed under `${libdir}` with the name `samdb`; the include line assumes public headers under `${includedir}`.

## Risks and edge cases
- Incorrect `libdir`, `includedir`, or `LIB_RPATH` substitutions break downstream builds or runtime loading.
- Removing `HAVE_IMMEDIATE_STRUCTURES=1` may change header-visible structure behavior for consumers.
- The template does not list transitive private libraries; if static linking is expected elsewhere, companion build metadata may be needed.

## Test signals
Useful checks are build-system generation of `samdb.pc`, `pkg-config --cflags --libs samdb` in an installed/staged tree, compiling a small consumer against `samdb` headers, and verifying runtime lookup when `@LIB_RPATH@` is expected to carry nonstandard library paths.
