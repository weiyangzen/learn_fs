## sources/distributed-fs/xrootd/src/XrdHttp/CMakeLists.txt

Purpose: builds and installs the XrdHttp utility shared library and HTTP protocol module when `BUILD_HTTP` is enabled.

Important APIs and control flow: the file returns immediately if HTTP is disabled. `XrdHttpUtils` is built as a shared library from checksum, extension handler, protocol, range, request, monitoring, security, static, tracing, utility, and header utility sources. It sets library version properties, links privately to `XrdServer`, `XrdUtils`, and `XrdCrypto`, and publicly to OpenSSL SSL/Crypto. It then builds module `${XrdHttp}` from `XrdHttpModule.cc`, links it against `XrdUtils` and `XrdHttpUtils`, sets `.so` suffix, and installs both targets to the library directory.

State and persistence: build artifacts are the shared `XrdHttpUtils` library and versioned HTTP module plugin. Install rules persist them in `${CMAKE_INSTALL_LIBDIR}`.

Dependencies and integration: integrates the HTTP protocol with the XRootD plugin loader. The comment notes that HTTP extension plugins are expected to link against `XrdHttpUtils` for `XrdHttpExt` implementations.

Risks and test signals: link visibility is important because plugins consume `XrdHttpUtils`; ABI changes in headers should be tested with downstream plugin builds. Build tests should cover `BUILD_HTTP=OFF`, shared library versioning, OpenSSL link propagation, and plugin suffix/name conventions.
