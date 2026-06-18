## sources/distributed-fs/xrootd/src/XrdEc/CMakeLists.txt

### Purpose
This build file defines the optional `XrdEc` shared library for erasure-coded client-side storage support.

### Important APIs, Types, and Functions
When `BUILD_XRDEC` is enabled, it builds `XrdEc` from configuration, object-layout, reader, redundancy provider, streaming writer, thread-pool, utility, and write-buffer sources. It links `XrdCl`, `XrdUtils`, and `${ISAL_LIBRARIES}`, and includes `${ISAL_INCLUDE_DIRS}`.

### Control Flow
The first guard returns immediately if `BUILD_XRDEC` is false. Otherwise the library target is created, linked, versioned, and installed together with its private headers.

### State and Persistence
Build state includes the shared-library target and installed private headers under `${CMAKE_INSTALL_INCLUDEDIR}/xrootd/private/XrdEc`. Runtime state is handled by the compiled sources.

### Dependencies and Integration Points
The library depends on ISA-L for erasure coding and CRC helpers, plus XrdCl/XrdUtils. XrdCl includes EC handler code that constructs `XrdEc::Reader`, `StrmWriter`, and `ObjCfg`.

### Risks and Edge Cases
If ISA-L include or library variables are misconfigured, the target will fail to build or link. Headers are installed under a private include path, indicating consumers should be internal XRootD components rather than stable public API users.

### Test Signals
`BUILD_XRDEC=ON` builds and installs `libXrdEc` with the expected SONAME/version. Link-time checks should confirm ISA-L symbols and XrdCl/XrdUtils dependencies resolve.
