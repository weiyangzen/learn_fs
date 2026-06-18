
## sources/storage-engines/wiredtiger/ext/compressors/zlib/CMakeLists.txt

Purpose: defines the zlib compressor build.

Integration: `HAVE_BUILTIN_EXTENSION_ZLIB` depends on `HAVE_LIBZ` and conflicts with `ENABLE_ZLIB`. The target `wiredtiger_zlib` is an `OBJECT` builtin or loadable `MODULE`, includes WiredTiger headers, links `wt::zlib`, applies C diagnostics, sets PIC, and installs only for dynamic extension builds.

State: no runtime state in CMake. Risks are dependency discovery and export-mode consistency. Test signals include configure failure without zlib, dynamic install checks, builtin link checks, and zlib compression-level config tests in the C file.
