# sources/distributed-fs/xrootd/src/CMakeLists.txt

## Purpose
This top-level source CMake file orchestrates XRootD library targets and subdirectories, including shared utility and server libraries.

## Important APIs, Types, and Functions
It configures PyPI build RPATHs, maps `XRDCL_LIB_ONLY` to `XRDCL_ONLY`, includes `XrdHeaders`, creates shared libraries `XrdUtils` and conditionally `XrdServer`, sets SOVERSION/VERSION properties, links platform/system dependencies, installs libraries, and adds many source subdirectories.

## Control Flow
Configuration first handles install RPATH. It always builds and installs `XrdUtils`, then adds common/client-related subdirectories including `XProtocol`, `XrdCl`, HTTP/S3 client pieces, and erasure coding. If `NOT XRDCL_ONLY`, it also builds `XrdServer` and adds server/plugin subdirectories such as auth, cms, ofs, oss, http, macaroons, voms, ceph, and scitokens.

## State and Persistence
Build state is CMake targets, link interfaces, RPATHs, and installed shared libraries. No runtime persistence.

## Dependencies and Integration Points
Depends on OpenSSL, threads, dl/socket/sendfile/systemd/atomic/extra platform libraries, and many internal XRootD subdirectories. It is the central integration point for client-only versus full server builds.

## Risks and Test Signals
RPATH handling differs for PyPI/macOS/non-macOS builds. `XRDCL_ONLY` gates large server functionality, so build matrix coverage is important. Test signals are successful client-only and full builds, installed library discovery, RPATH correctness for Python/plugin packaging, and link correctness with optional systemd/platform libraries.
