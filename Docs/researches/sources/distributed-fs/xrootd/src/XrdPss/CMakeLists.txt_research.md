<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdPss/CMakeLists.txt

Purpose: Defines the XrdPss proxy storage system plugin build target. It creates a versioned module library and links it against the POSIX client layer, utility library, and server library.

Important APIs/types/functions: `set(XrdPss XrdPss-${PLUGIN_VERSION})` names the module. `add_library(... MODULE ...)` includes `XrdPss.cc/.hh`, async files, checksum files, config, trace, URL info, and utility sources. `target_link_libraries(${XrdPss} PRIVATE XrdPosix XrdUtils XrdServer)` supplies dependencies. `install(TARGETS ... LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})` installs the plugin.

Control flow and state: Build-system only. It does not configure runtime state but determines which source units are packaged into `libXrdPss` and which symbols/plugins are available.

Dependencies/integration: The target depends directly on `XrdPosix`, so PSS can call `XrdPosixXrootd` and `XrdPosixExtra`. It also requires server-side OSS/OFS/SFS interfaces from `XrdServer` and utility/config support from `XrdUtils`.

Risks and test signals: Omitting a source breaks plugin entrypoints such as `XrdOssGetStorageSystem2` or checksum initialization. Tests should include CMake configure/build, module install path verification, plugin loading by XRootD server, and link checks for PSS config/URL utility symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/CMakeLists.txt -->
