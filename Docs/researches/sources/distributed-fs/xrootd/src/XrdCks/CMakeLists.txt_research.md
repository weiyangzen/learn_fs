# sources/distributed-fs/xrootd/src/XrdCks/CMakeLists.txt

Purpose: adds XrdCks checksum framework sources to `XrdUtils` and builds the zlib-compatible CRC32 checksum calculator as a loadable module.

Important build APIs: `target_sources(XrdUtils PRIVATE ...)` lists manager, loader, algorithm, assist, data, wrapper, and xattr helper files. `set(XrdClsCalczcrc32 XrdCksCalczcrc32-${PLUGIN_VERSION})` names the plugin module. `add_library(... MODULE XrdCksCalczcrc32.cc)`, `target_link_libraries(... PRIVATE XrdUtils ZLIB::ZLIB)`, and `install(TARGETS ... LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})` define build and install behavior.

Control flow and integration: most checksum code is compiled into `XrdUtils`; the zlib CRC32 implementation remains a plugin that exports `XrdCksCalcInit`.

State and persistence: build metadata only. Runtime checksum state lives in calculator and manager classes.

Dependencies: requires `ZLIB::ZLIB` for the zcrc32 plugin and the project-defined `PLUGIN_VERSION`, `XrdUtils`, and install directory variables.

Risks and test signals: build tests should verify plugin naming, module install path, and zlib discovery. ABI tests should ensure sources added to `XrdUtils` match headers exported to plugin users.
