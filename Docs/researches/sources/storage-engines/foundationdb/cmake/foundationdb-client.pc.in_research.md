# sources/storage-engines/foundationdb/cmake/foundationdb-client.pc.in

## Purpose
Pkg-config template for the FoundationDB C client library.

## Important APIs, Types, and Functions
Defines `libdir`, `includedir`, package `Name`, `Description`, `Version`, `Libs`, and `Cflags`.

## Control Flow and Integration
`fdb_configure_and_install` configures this per package/install destination so C clients can discover `-lfdb_c` and include paths.

## State and Persistence
Depends on `LIB_DIR`, `INCLUDE_DIR`, and `FDB_VERSION` substitutions.

## Dependencies
Configured `.pc` files persist in package install trees.

## Risks and Test Signals
Risks include wrong libdir for EL9 lib64 layouts or versioned packages. Test signal is `pkg-config --libs --cflags foundationdb-client` after install.
