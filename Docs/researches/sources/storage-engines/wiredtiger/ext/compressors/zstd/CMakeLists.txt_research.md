
## sources/storage-engines/wiredtiger/ext/compressors/zstd/CMakeLists.txt

Purpose: defines the Zstandard compressor build.

Integration: `HAVE_BUILTIN_EXTENSION_ZSTD` depends on `HAVE_LIBZSTD`; builtin and `ENABLE_ZSTD` are mutually exclusive. It builds `wiredtiger_zstd` as builtin `OBJECT` or dynamic `MODULE`, includes WiredTiger headers, links `wt::zstd`, applies C diagnostics, sets PIC, and installs the dynamic target.

State: no runtime state here. Risks are dependency discovery and symbol/export mode consistency. Test signals include configure-time dependency failures, builtin/dynamic builds, and extension load with context-pool initialization from `zstd_compress.c`.
