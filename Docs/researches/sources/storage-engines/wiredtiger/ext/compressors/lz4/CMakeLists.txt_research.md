
## sources/storage-engines/wiredtiger/ext/compressors/lz4/CMakeLists.txt

Purpose: defines the LZ4 compressor build. `HAVE_BUILTIN_EXTENSION_LZ4` is gated on `HAVE_LIBLZ4`; builtin and dynamic `ENABLE_LZ4` are mutually exclusive.

Integration: builds `wiredtiger_lz4` from `lz4_compress.c` as either `OBJECT` for builtin use or `MODULE` for loadable extension use. It includes WiredTiger generated/config headers, links `wt::lz4`, applies C diagnostic flags, marks the target PIC, and installs only when `ENABLE_LZ4` is on.

State: no runtime state. Risks are dependency discovery and keeping builtin/module symbol behavior aligned with `lz4_compress.c`. Test signals include configuring dependency-missing builds, builtin builds, module builds, and installation layout checks.
