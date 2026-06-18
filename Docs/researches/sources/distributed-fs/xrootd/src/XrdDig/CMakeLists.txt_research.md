## sources/distributed-fs/xrootd/src/XrdDig/CMakeLists.txt

### Purpose
This build fragment adds the built-in dig file system implementation to the `XrdServer` target.

### Important APIs, Types, and Functions
It contributes `XrdDigAuth.cc/.hh`, `XrdDigConfig.cc/.hh`, and `XrdDigFS.cc/.hh` as private sources. There are no exported CMake options in this file.

### Control Flow
When the parent `src/CMakeLists.txt` adds the `XrdDig` subdirectory, this file unconditionally appends the dig sources to `XrdServer`.

### State and Persistence
No runtime state is handled here. Build state is limited to target source membership.

### Dependencies and Integration Points
The digFS code is compiled directly into `XrdServer`; runtime integration happens through `XrdDigGetFS` and xrootd configuration code in `XrdXrootdConfig.cc`.

### Risks and Edge Cases
Because this is private target source inclusion rather than a separate library, source-level dependencies and platform guards must be correct in the `.cc` files. Build failures in digFS affect the server target.

### Test Signals
Successful configuration and compilation of `XrdServer` with the XrdDig sources is the primary signal. Runtime coverage comes from xrootd configuration tests that enable the digFS path.
