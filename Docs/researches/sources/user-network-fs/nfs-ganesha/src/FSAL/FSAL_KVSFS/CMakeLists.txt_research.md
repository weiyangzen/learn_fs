## sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_KVSFS/CMakeLists.txt

Purpose: This CMake file builds the KVSFS FSAL plugin module. It wires KVSFS source files into a shared module named `fsalkvsfs`, links it to the KVS namespace library and hiredis, assigns module version metadata, and installs it into the configured FSAL destination.

Important build definitions: If `KVSFS_PREFIX` is set, it appends include and library flags using `${KVSNS_PREFIX}/include` and `${KVSNS_PREFIX}/lib`. `fsalkvsfs_LIB_SRCS` includes `kvsfs_fsal_internal.c`, `kvsfs_main.c`, `kvsfs_export.c`, `kvsfs_handle.c`, `kvsfs_file.c`, `kvsfs_xattrs.c`, `kvsfs_mds.c`, and `kvsfs_ds.c`. `add_library(fsalkvsfs MODULE ...)` creates the dynamically loaded FSAL module. `target_link_libraries` links `kvsns`, `hiredis`, and `${SYSTEM_LIBRARIES}`. `set_target_properties` sets version `4.2.0` and soversion `4`. `install(TARGETS fsalkvsfs COMPONENT fsal DESTINATION ${FSAL_DESTINATION})` installs the plugin.

Control flow and state: The file has straightforward configure-time control: optional prefix flags, source aggregation, target creation, sanitizer hook, link libraries, properties, and install rule. Runtime FSAL behavior is defined in the C sources.

Persistence behavior: Build state consists of compiler/linker flags, produced module artifacts, and installation into the FSAL plugin destination. No source-level runtime persistence is encoded here.

Dependencies and integration points: It integrates with the repository's global CMake macros, especially `add_sanitizers`, `SYSTEM_LIBRARIES`, and `FSAL_DESTINATION`. It requires `kvsns` headers/libraries and `hiredis`, implying KVSFS is backed by an external key-value namespace implementation that likely uses Redis or hiredis-compatible transport.

Risks: The conditional checks `KVSFS_PREFIX` but uses `KVSNS_PREFIX`, which may be intentional naming or a variable mismatch. More clearly, `add_sanitizers(fsalceph)` references `fsalceph` instead of `fsalkvsfs`, so sanitizer instrumentation may be applied to the wrong target or fail depending on macro behavior. Appending `-L` to `CMAKE_C_FLAGS` is also nonstandard because library search paths are link flags, not compile flags. Test signals include configuring with and without prefix variables, verifying `fsalkvsfs` links to the intended libraries, ensuring sanitizer builds actually instrument `fsalkvsfs`, and installing/loading the module in a Ganesha test instance.
