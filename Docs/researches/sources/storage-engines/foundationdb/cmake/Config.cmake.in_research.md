# sources/storage-engines/foundationdb/cmake/Config.cmake.in

## Purpose
Template for an installed FoundationDB CMake package config that includes the generated exported target file.

## Important APIs, Types, and Functions
Contains one `include("${CMAKE_CURRENT_LIST_DIR}/@targets_export_name@.cmake")` directive.

## Control Flow and Integration
`fdb_configure_and_install` configures this template per package/install layout so downstream CMake projects can import FoundationDB targets from the install tree.

## State and Persistence
Depends on `targets_export_name` substitution and corresponding installed export files.

## Dependencies
No runtime state; configured package files persist in generated/install directories.

## Risks and Test Signals
Risks are broken installed package discovery if export name or destination changes. Test signal is a downstream `find_package` or include of the installed config file.
