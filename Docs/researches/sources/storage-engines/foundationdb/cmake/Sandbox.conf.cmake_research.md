# sources/storage-engines/foundationdb/cmake/Sandbox.conf.cmake

## Purpose
Template for a local sandbox `foundationdb.conf` used by build-tree development clusters.

## Important APIs, Types, and Functions
Defines `[fdbmonitor]`, `[general]`, default `[fdbserver]`, and `[fdbserver.4000]` sections with build-tree binary, cluster, data, and log paths.

## Control Flow and Integration
Configured by CMake for local cluster/sandbox runs so fdbmonitor launches the just-built `fdbserver` with build-local storage and logs.

## State and Persistence
Depends on `CMAKE_BINARY_DIR` substitution and built `bin/fdbserver`.

## Dependencies
Runtime state is external to the template: generated config, cluster file, data dir, and log dir under the CMake binary tree.

## Risks and Test Signals
Risks include build-tree path invalidation after moving directories and single-process defaults not matching production. Test signal is local sandbox cluster startup.
