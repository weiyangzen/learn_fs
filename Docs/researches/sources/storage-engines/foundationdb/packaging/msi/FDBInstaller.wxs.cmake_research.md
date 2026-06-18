<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/msi/FDBInstaller.wxs.cmake -->
# Research: sources/storage-engines/foundationdb/packaging/msi/FDBInstaller.wxs.cmake

## Purpose
WiX installer template for the Windows FoundationDB MSI, including client files, server service, config/data/log directories, registry values, environment variables, and Python binding installation.

## Important APIs, Types, And Functions
Defines product metadata, upgrade code, generated paths, known Python versions, component GUIDs, features, service install/control entries, IniFile edits, Python compile custom actions, random cluster-file creation, and new database configuration custom action.

## Control Flow
At install time WiX installs binaries and libraries under Program Files, creates CommonAppData `foundationdb` config/log/data directories, installs and starts `fdbmonitor` as a Windows service when the server feature is selected, optionally creates `fdb.cluster`, updates `foundationdb.conf`, compiles Python files, and runs `fdbcli configure new single memory; status` after services start.

## State And Persistence Behavior
Persistent state includes Program Files contents, PATH and `FOUNDATIONDB_INSTALL_PATH`, HKLM client/server version registry keys, CommonAppData config/data/log directories marked permanent, a Windows service, generated cluster file, and Python package files in detected Python installations.

## Dependencies And Integration Points
Depends on WiX schema/extensions, generated build paths, FoundationDB binaries, Python binding files, Python registry keys, and Windows service manager. This is the authoritative Windows MSI contract used by the CMake packaging target.

## Risks And Edge Cases
Permanent config/data/log components preserve state across uninstall and upgrade, which is intentional but can surprise tests. Python support lists old versions and custom install paths. Custom actions rely on command quoting and service readiness. Random cluster-file generation uses `%RANDOM%` rather than cryptographic entropy.

## Test Signals
Test signal is mainly MSI build/install smoke testing. The template has no direct parser tests; service startup and `ConfigureNewDatabase` success are the important acceptance checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/msi/FDBInstaller.wxs.cmake -->
