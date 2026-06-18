
## sources/storage-engines/wiredtiger/ext/compressors/snappy/CMakeLists.txt

Purpose: defines the Snappy compressor build with builtin and dynamic modes.

Integration: `HAVE_BUILTIN_EXTENSION_SNAPPY` depends on `HAVE_LIBSNAPPY`; builtin and `ENABLE_SNAPPY` are mutually exclusive. The build creates `wiredtiger_snappy` as `OBJECT` or `MODULE`, includes WiredTiger headers, links `wt::snappy`, applies C diagnostics, sets PIC, and installs in dynamic-extension mode.

State: none at build time. Risks are dependency detection and keeping module/builtin export decisions aligned with the C source. Test signals include configure-time dependency failure, builtin symbol exclusion, module installation, and load-time Snappy round trips.
