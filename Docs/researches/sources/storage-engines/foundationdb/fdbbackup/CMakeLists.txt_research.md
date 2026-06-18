# sources/storage-engines/foundationdb/fdbbackup/CMakeLists.txt

## Purpose
Defines backup-related executables, packaging aliases, and tests for FoundationDB backup tooling.

## Important APIs, Types, and Functions
Builds `fdbbackup` from `Decode.cpp` and `backup.cpp`, `fdbconvert` from `FileConverter.cpp`, and `fdbdecode` from `Decode.cpp` plus `FileDecoder.cpp`. Installs `fdbbackup` under aliases `backup_agent`, `fdbrestore`, `dr_agent`, and `fdbdr`. Adds `backup_tests`, `fdbdecode_tests`, and shell tests for directory/blob/S3 backup flows.

## Control Flow
CMake declares targets, include directories, and links. Under `NOT OPEN_FOR_IDE`, it adds install rules, symlinks, test binaries, and CTest entries. Optional gperftools linkage is added when found. Non-Windows builds register shell integration tests.

## State and Persistence Behavior
Creates build/install/test state and symlinked package artifacts. Runtime backup state is handled by the executables, not CMake.

## Dependencies and Integration Points
Depends on FoundationDB CMake helpers, `fdbclient`, optional gperftools, sanitizer environment settings, and test scripts under `fdbbackup/tests`.

## Risks
One binary backs multiple installed command names, so packaging mistakes affect several tools. Some tests are skipped in IDE/Windows modes. Non-debug installs depend on stripped package-bin artifacts.

## Test Signals
Build all targets and run `BackupTests`, `FileDecoderTests`, directory backup, blob backup restore, and S3 bulk dump/load tests where credentials/environment exist.
