# sources/storage-engines/foundationdb/cmake/CPackConfig.cmake

## Purpose
Selects CPack component sets and package metadata inputs based on the active package generator.

## Important APIs, Types, and Functions
Sets `CPACK_PACKAGING_INSTALL_PREFIX`, `CPACK_COMPONENTS_ALL`, `CPACK_RESOURCE_FILE_README`, `CPACK_RESOURCE_FILE_LICENSE`, and `CPACK_STRIP_FILES` for RPM, DEB, and TGZ branches.

## Control Flow and Integration
`InstallLayout.cmake` configures this file into the build packaging directory and assigns it as `CPACK_PROJECT_CONFIG_FILE`. At CPack runtime, the script matches `CPACK_GENERATOR` and enables the correct client/server/versioned components.

## State and Persistence
Depends on CPack variables, project `README.md` and `LICENSE`, and component names created by install rules.

## Dependencies
No long-lived state beyond CPack variables; effects are consumed by package generation.

## Risks and Test Signals
Risks are unsupported generator fatal errors and component-name drift between install rules and package config. Test signals are successful RPM/DEB/TGZ package creation with expected components.
