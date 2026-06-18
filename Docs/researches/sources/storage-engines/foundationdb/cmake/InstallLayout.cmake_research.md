# sources/storage-engines/foundationdb/cmake/InstallLayout.cmake

## Purpose
Defines FoundationDB package layouts, CPack metadata, multiversion scripts, Docker packaging copies, and server/client install destinations.

## Important APIs, Types, and Functions
Includes `FDBInstall`, registers `TGZ`, `DEB`, `EL9`, and `VERSIONED` packages, sets logical dirs, configures CPack RPM/DEB/TGZ variables, and installs configuration/service/init files.

## Control Flow and Integration
The module maps package types to filesystem destinations, configures multiversion postinst/prerm scripts, sets component dependencies and filenames, creates empty log/data/etc dirs, excludes RPM auto filelist paths, and installs server config/service assets.

## State and Persistence
Depends on `FDBInstall.cmake`, packaging templates/scripts, project version variables, CPack, systemd/init assets, and package component names.

## Dependencies
State persists in package install variables, generated packaging scripts under `packaging/multiversion`, copied Docker assets, random cluster description cache strings, and CPack variables.

## Risks and Test Signals
Risks include duplicate symlink helper definitions, package filename/version drift, architecture-specific Debian naming, and random cluster descriptions in cache. Test signals are CPack RPM/DEB/TGZ outputs and package install/uninstall tests.
