# sources/storage-engines/foundationdb/cmake/FDBInstall.cmake

## Purpose
Provides generic installation helper functions used by FoundationDB package layout code.

## Important APIs, Types, and Functions
Defines package/dir registries, symlink helpers, `pop_front`, `install_destinations`, `get_install_dest`, `copy_install_destinations`, `fdb_configure_and_install`, and `fdb_install`.

## Control Flow and Integration
`InstallLayout.cmake` registers package names and logical install dirs, then these helpers expand logical destinations into per-package `install()` calls and configured template installs. Symlink helpers synthesize component-specific relative symlinks.

## State and Persistence
Depends on CMake install rules, package/component names, and caller-defined `generated_dir`.

## Dependencies
State is stored in parent-scope variables like `FDB_INSTALL_PACKAGES`, `FDB_INSTALL_DIRS`, and private `__install_dest_<pkg>_<dir>` variables; generated configured files go under `generated_dir`.

## Risks and Test Signals
Risks include duplicated symlink helper definitions with `InstallLayout.cmake`, platform-condition confusion, and fatal errors for unknown logical dirs. Test signals are install manifests and package contents matching expected paths.
