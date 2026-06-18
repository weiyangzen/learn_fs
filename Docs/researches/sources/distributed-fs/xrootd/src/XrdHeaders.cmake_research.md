## sources/distributed-fs/xrootd/src/XrdHeaders.cmake

Purpose: defines installation of public and private XRootD headers. It is a build-system manifest that controls which headers are exposed under `${CMAKE_INSTALL_INCLUDEDIR}/xrootd` and its `private` subdirectory.

Important APIs and control flow: `install_headers(destination files)` iterates a header list, extracts the subdirectory with a regex, and installs each file under the matching destination subtree. The script installs generated `XrdVersion.hh`, defines `XROOTD_PUBLIC_HEADERS`, conditionally appends server-only headers when `NOT XRDCL_ONLY`, defines `XROOTD_PRIVATE_HEADERS`, conditionally appends private server/plugin headers and VOMS headers, then calls `install_headers()` for public and private groups.

State and persistence: persistent effect is CMake install metadata and installed header layout. No runtime state exists.

Dependencies and integration: consumed by the top-level XRootD build. Variables include `CMAKE_BINARY_DIR`, `CMAKE_INSTALL_INCLUDEDIR`, `XRDCL_ONLY`, and `BUILD_VOMS`. The manifest includes `XrdHttp/XrdHttpSecXtractor.hh` publicly and `XrdHttp/XrdHttpExtHandler.hh` privately, affecting plugin ABI consumers.

Risks and test signals: duplicate public entries exist for some headers in server-only append blocks, which CMake install may tolerate but packaging tests should catch. The regex assumes paths contain a directory component. Tests should validate install manifests for client-only and full builds, private/public ABI expectations, and generated version header presence.
