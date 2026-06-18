# sources/distributed-fs/xrootd/src/XrdCl/CMakeLists.txt

Purpose: defines the XrdCl client library build, optional erasure-coding sources, public/private header installation, and client executables.

Important APIs/targets: `add_library(XrdCl SHARED ...)`, `target_link_libraries` against XML, utilities, uuid, zlib, OpenSSL, threads, dl, and extras; optional `BUILD_XRDEC` source inclusion and `WITH_XRDEC`; install rules for public headers under `xrootd/XrdCl` and private headers under `xrootd/private/XrdCl`; optional `xrdcp` and `xrdfs` executables when `XRDCL_LIB_ONLY` is false.

Control flow/state: CMake exits early unless `ENABLE_XRDCL` is enabled. Library ABI is set by `SOVERSION` and `VERSION`. Persistence is build/install metadata rather than runtime state. Integration points span most XrdCl sources, OpenSSL, ZLIB, readline/ncurses for `xrdfs`, and symlink creation for `xrdcopy`. Risks: install header classification affects downstream consumers, optional EC dependency correctness, and install-time symlink behavior under DESTDIR. Test signals: configure matrices for enabled/disabled client library, EC on/off, lib-only mode, and install manifest validation.
