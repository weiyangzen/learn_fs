# sources/storage-engines/foundationdb/fdbclient/azurestorage.cmake

Purpose: CMake helper project for fetching Azure Storage C++ Lite as an external dependency.

Important APIs and control flow: declares `cmake_minimum_required(3.13)`, project `azurestorage-download`, includes `ExternalProject`, and defines `ExternalProject_Add(azurestorage)`. The external project is pinned to `https://github.com/Azure/azure-storage-cpplite.git` at commit `11e1f98b021446ef340f4886796899a6eb1ad9a5`.

State and persistence: source and binary directories are under the current binary directory as `azurestorage-src` and `azurestorage-build`. The declared byproduct is `libazure-storage-lite.a`. Configure/build/install/test commands are empty, so this file's role is download/source staging rather than building the library itself.

Dependencies and integration: used by the FoundationDB build when Azure blob backup support needs the cpplite source. It depends on CMake `ExternalProject` and network access during configure/build dependency resolution.

Risks: supply-chain behavior depends on GitHub availability and the pinned commit remaining fetchable. Empty build commands mean consumers must know where and how to consume the staged source or byproduct. Any change to the upstream repository layout can break downstream assumptions even with the pin if submodules or generated files are involved.

Test signals: validation is at CMake configure/generate time and in builds that require Azure storage; there are no direct tests in this file.
