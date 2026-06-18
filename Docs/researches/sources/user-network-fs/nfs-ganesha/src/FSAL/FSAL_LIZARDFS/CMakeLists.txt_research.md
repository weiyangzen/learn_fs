# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/CMakeLists.txt

Purpose: Builds the LizardFS FSAL as a Ganesha loadable module.

Important APIs and types: The build target is `fsallizardfs`, a `MODULE` library with sources `context_wrap.c`, `ds.c`, `export.c`, `handle.c`, `lzfs_acl.c`, `lzfs_internal.c`, `main.c`, `mds_export.c`, and `mds_handle.c`, plus their headers. It applies `-D__USE_GNU` and `${LIZARDFS_CFLAGS}` and links `${SYSTEM_LIBRARIES}` and `${LIZARDFS_CLIENT_LIB}`.

Control flow: CMake collects the FSAL sources into `fsallizardfs`, applies sanitizer integration with `add_sanitizers(fsallizardfs)`, sets module version `3.12.0`/SOVERSION `3`, and installs it to `${FSAL_DESTINATION}` under component `fsal`.

State and persistence: No runtime state. The file controls which implementation units are compiled into the plugin and therefore which FSAL operations are available.

Dependencies and integration: Requires the LizardFS client library and headers to be available in the parent build. It relies on Ganesha's module loading convention and sanitizer helper macro.

Risks: Missing `LIZARDFS_CLIENT_LIB` or mismatched `LIZARDFS_CFLAGS` will fail link/compile. The target does not link `ganesha_nfsd` explicitly, unlike FSAL_MEM, so symbol resolution relies on module loading and parent link policy. Version/SOVERSION must remain consistent with deployment packaging expectations.

Test signals: Configure with and without LizardFS client development files, build with sanitizers enabled, inspect undefined symbols in the module, install packaging paths, and run a Ganesha startup smoke test loading `fsallizardfs`.
