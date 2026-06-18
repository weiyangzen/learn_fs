# sources/distributed-fs/xrootd/src/XrdAcc/CMakeLists.txt

## Purpose

`XrdAcc/CMakeLists.txt` wires the XrdAcc authorization sources and headers into the `XrdServer` target. The file was read completely.

## Important APIs, Types, and Functions

It calls `target_sources(XrdServer PRIVATE ...)` and lists the access engine, audit object, auth DB interface, authorization plugin interface, auth file implementation, capabilities, configuration, entity attributes, groups, and privilege definitions.

## Control Flow

There is no runtime control flow. During configuration/generation, CMake attaches these files to `XrdServer`.

## State and Persistence Behavior

The build graph state is the only state affected. No installation rule is declared here; installation/export behavior is inherited from higher-level targets.

## Dependencies and Integration Points

This file integrates the XrdAcc module with the server library/executable target. It assumes `XrdServer` exists in the parent CMake scope.

## Risks and Edge Cases

Adding a new XrdAcc file without updating this list will omit it from `XrdServer`. Public header installation, if expected, must be handled elsewhere. Target existence is order-sensitive.

## Test Signals

CMake configure/build tests should validate `XrdServer` compiles with all listed files. Packaging tests should confirm authorization headers are exported as intended by the broader build.
