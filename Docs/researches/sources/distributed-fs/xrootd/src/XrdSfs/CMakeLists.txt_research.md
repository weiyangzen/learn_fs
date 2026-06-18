# sources/distributed-fs/xrootd/src/XrdSfs/CMakeLists.txt

## Purpose
Declares the Standard File System sources that are compiled directly into the `XrdServer` target.

## Important APIs, Types, And Functions
The file contributes `XrdSfsNative.cc`, `XrdSfsInterface.cc`, `XrdSfsXio.cc`, and their public headers to `target_sources(XrdServer PRIVATE ...)`. It does not define runtime APIs itself.

## Control Flow
CMake appends the SFS implementation files to the server target during configuration. Headers are listed as private source entries for IDE visibility and dependency tracking.

## State And Persistence
No runtime state. Build state is limited to target source membership.

## Dependencies And Integration Points
Integrates the SFS native adapter and base interface with the XRootD server build. Because the files are `PRIVATE`, consumers include installed/exported headers through other packaging rules rather than inheriting these target sources.

## Risks And Edge Cases
Missing a header or implementation here can break server builds or hide a changed file from IDE/source package expectations. The file does not list `XrdSfsDio.hh`, although that header is part of the API and included elsewhere; packaging rules should be checked if header installation depends on this list.

## Test Signals
Configure and build `XrdServer`, then verify source-file dependency tracking after touching `XrdSfsInterface.hh`, `XrdSfsNative.cc`, and `XrdSfsXio.cc`.
