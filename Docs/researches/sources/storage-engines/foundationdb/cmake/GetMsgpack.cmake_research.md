# sources/storage-engines/foundationdb/cmake/GetMsgpack.cmake

## Purpose
Normalizes msgpack C++ dependency discovery behind an interface target.

## Important APIs, Types, and Functions
Finds legacy/new msgpack package names, creates `msgpack` interface target, links to detected imported targets, or downloads msgpack-c 3.3.0 with SHA256 via ExternalProject.

## Control Flow and Integration
Downstream code links `msgpack`; the module hides whether the dependency came from config packages or external headers.

## State and Persistence
Depends on msgpack CMake packages or the pinned release tarball.

## Dependencies
State includes ExternalProject source dir and `msgpack` interface include directories/dependencies.

## Risks and Test Signals
Risks include multiple msgpack package naming variants and header-only external project not rebuilding if include path changes. Test signal is C++ compilation using msgpack headers.
