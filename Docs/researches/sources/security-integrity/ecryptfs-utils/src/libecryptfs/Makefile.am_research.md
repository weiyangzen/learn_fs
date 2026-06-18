# sources/security-integrity/ecryptfs-utils/src/libecryptfs/Makefile.am

## Purpose
Automake definition for building the shared `libecryptfs.la` library and installing its pkg-config metadata. It lists the C implementation units that form the library and wires crypto/keyutils compiler and linker flags into the build.

## Important APIs, types, and functions
- `lib_LTLIBRARIES = libecryptfs.la` declares the installed libtool library.
- `pkgconfig_DATA = libecryptfs.pc` installs the pkg-config file generated from `libecryptfs.pc.in`.
- `libecryptfs_la_SOURCES` pulls in mount helpers, messaging, packets, miscdev, sysfs, key management, decision graph parsing, module manager, key modules, and stat parsing.
- `libecryptfs_la_LDFLAGS` carries libtool version-info and `-no-undefined`.
- `libecryptfs_la_CFLAGS` and `libecryptfs_la_LIBADD` apply `CRYPTO_*` and `KEYUTILS_*` configure results.

## Control flow
There is no runtime control flow. Build flow is source compilation into one libtool library, link with crypto and keyutils dependencies, and optional `splint` static analysis over local C files.

## State and persistence behavior
No application state is handled. The file controls installed artifacts: the shared library and pkg-config metadata.

## Dependencies and integration points
Connects the source files in this subset into the installed library consumed by mount helpers, PAM integration, SWIG bindings, and other eCryptfs utilities. The built-in passphrase module is compiled directly into the library, while dynamic key modules are discovered at runtime by `key_mod.c`.

## Risks and edge cases
Adding a source file without updating this list can silently omit functionality from the library. The direct reference to the passphrase key module couples libecryptfs to source layout under `src/key_mod`. ABI versioning depends on configured `LIBECRYPTFS_LT_*` values being updated when public symbols or struct contracts change.

## Test signals
Build-system validation should run autoreconf/configure plus `make` and confirm `libecryptfs.la` links with no undefined symbols. `pkg-config --libs --cflags libecryptfs` after installation should expose keyutils and include flags as expected.
