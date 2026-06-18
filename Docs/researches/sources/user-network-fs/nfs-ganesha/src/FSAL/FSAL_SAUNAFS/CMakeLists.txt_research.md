# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/CMakeLists.txt

This build file defines the SaunaFS FSAL shared module `fsalsaunafs`. It is the build integration point that collects the FSAL implementation files, links against the SaunaFS client library, attaches optional sanitizer/LTTng behavior, and installs the resulting module into the configured FSAL destination.

The source list includes the files in this research item plus adjacent support files: ACL handling, internal error/context helpers, and private type headers. `add_library(fsalsaunafs MODULE ...)` builds a dynamically loaded Ganesha FSAL module. `target_link_libraries(fsalsaunafs ${SAUNAFS_CLIENT_LIB})` is the critical external dependency. `add_sanitizers` applies the repository's sanitizer wrapper. When `USE_LTTNG` is enabled, the target depends on generated trace headers and includes generated CMake file properties. The module version and soversion are set to `4.0.0` and `4`.

There is no runtime state in this file, but it controls which implementation objects are present in the module. Missing any of `context_wrap`, `handle`, `export`, `ds`, or `mds_*` would remove core runtime capabilities.

Dependencies are CMake variables from the parent build, the SaunaFS client library, sanitizer macros, LTTng generation, and `FSAL_DESTINATION`. Integration is with Ganesha's plugin loading convention; the FSAL name in `main.c` expects a matching shared library.

Risks include stale source lists when new implementation files are added, unresolved `${SAUNAFS_CLIENT_LIB}` configuration, and trace-generation ordering issues under `USE_LTTNG`. Test signals are configure/build with and without LTTng, sanitizer builds, install-tree validation, and module load tests confirming `libfsalsaunafs.so` exports the expected init/fini symbols.
