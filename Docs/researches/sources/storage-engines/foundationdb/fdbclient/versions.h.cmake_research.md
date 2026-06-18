# sources/storage-engines/foundationdb/fdbclient/versions.h.cmake

## Purpose
This CMake template generates a tiny C/C++ header containing FoundationDB version and package-name macros.

## Important APIs, Types, And Functions
It emits `FDB_VT_VERSION` from `${FDB_VERSION}` and `FDB_VT_PACKAGE_NAME` from `${FDB_PACKAGE_NAME}` behind `#pragma once`.

## Control Flow
CMake configures the file by substituting variables during the build. Runtime code includes the generated header and reads compile-time string macros.

## State And Persistence Behavior
There is no runtime state. The generated header persists build metadata in the build output.

## Dependencies And Integration Points
It depends on the build system defining `FDB_VERSION` and `FDB_PACKAGE_NAME`. Consumers can use it to stamp binaries or generated versioned artifacts.

## Risks And Edge Cases
Missing or malformed CMake variables would produce empty or invalid macro strings. Because this is a template, source review must distinguish template placeholders from final generated values.

## Test Signals
Build tests should verify the configured header exists and contains the expected version/package values for a given build configuration.
