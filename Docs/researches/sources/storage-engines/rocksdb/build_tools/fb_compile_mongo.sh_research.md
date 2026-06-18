# sources/storage-engines/rocksdb/build_tools/fb_compile_mongo.sh research

Purpose: `fb_compile_mongo.sh` builds MongoDB against a RocksDB checkout using Meta fbcode compiler and dependency settings. It is a specialized integration helper for the historical MongoDB/RocksDB storage engine path.

Important APIs: configuration is through environment variables and script arguments. `ROCKSDB_PATH` defaults to `~/rocksdb`. `ALLOC` selects allocator behavior; `jemalloc` is translated to Mongo's `system` allocator plus explicit whole-archive jemalloc linking. Remaining command-line arguments are forwarded to `scons`.

Control flow: the script exits on error, sources `fbcode_config4.8.1.sh` from the RocksDB path, prepares a static dependency directory with symlinks to snappy and lz4 libraries, builds extra linker flags, detects older Mongo 3.0 by absence of `version.json`, and then invokes `scons` with compiler, linker, library, include, optimization, allocator, and warning options.

State and persistence: it creates `build/static_library_dependencies` and symlinks inside it. The main persistence is Mongo build output created by `scons`.

Dependencies and integration: it depends on shell, fbcode config files, RocksDB static/shared libraries, MongoDB's `scons` build, snappy/lz4 libraries, and a Mongo source checkout as current directory.

Risks and test signals: the script is tightly coupled to old Mongo and old fbcode config names. Several variables are unquoted. `source` is used under `/bin/sh`, which assumes a shell compatible with that builtin. Tests require an internal environment; practical signals are successful `scons` configuration, symlink creation, and Mongo binaries linking with RocksDB.
