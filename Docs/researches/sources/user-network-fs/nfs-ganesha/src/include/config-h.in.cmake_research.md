# sources/user-network-fs/nfs-ganesha/src/include/config-h.in.cmake

## Purpose
`config-h.in.cmake` is the CMake template for generated `config.h`. It centralizes version strings, install/runtime paths, OS markers, and build feature macros that conditionally compile large parts of NFS-Ganesha.

## Important APIs, Types, And Functions
The key macro helper is `GSH_CHECK_VERSION`. Version macros include `GANESHA_VERSION_MAJOR`, `GANESHA_VERSION_MINOR`, `GANESHA_EXTRA_VERSION`, `GANESHA_VERSION`, `GANESHA_BUILD_RELEASE`, `VERSION_COMMENT`, `_GIT_HEAD_COMMIT`, `_GIT_DESCRIBE`, and `BUILD_HOST`. Feature macros include protocol support (`_USE_NFS3`, `_USE_NFS_RDMA`, `_USE_NLM`, `_USE_RQUOTA`, `_USE_9P`), dependencies (`USE_DBUS`, `HAVE_KRB5`, `USE_CAPS`, `USE_LTTNG`, `USE_MONITORING`), FSAL/ACL/Ceph/Gluster features, debug/sanitizer toggles, and `RADOS_URLS`. Path macros include `GANESHA_CONFIG_PATH`, `GANESHA_PIDFILE_PATH`, `NFS_V4_RECOV_ROOT`, `NFS_V4_RECOV_DIR`, `NFS_V4_OLD_DIR`, and `DEFAULT_NFS_CCACHE_DIR`.

## Control Flow
CMake expands `@...@` substitutions and `#cmakedefine` entries into concrete `#define` or commented-out macros. Downstream C files use these macros for preprocessor conditionals, not runtime branching.

## State And Persistence
The generated header persists build-time configuration into every compiled object. It embeds filesystem paths, module location, git/build identity, and feature decisions. Runtime persistence is indirect through code enabled by these macros.

## Dependencies And Integration Points
Almost every project header includes `config.h` directly or indirectly. It gates OS-specific headers in `extended_types.h`, optional RADOS URL declarations, FSAL features in `fsal.h` consumers, protocol compilation, debug code, and sanitizer/dlopen flags.

## Risks
Mismatched generated config and installed modules can break dynamic loading or feature assumptions. Path macros are compiled in, so packaging mistakes affect default config, pidfile, recovery, and module locations. Feature macro combinations need broad build coverage; for example `SANITIZE_ADDRESS` changes dlopen flags and `RADOS_URLS` changes URL provider behavior.

## Test Signals
Test signals are mostly build/configuration matrix checks: minimal build, Linux/FreeBSD/Darwin where supported, DBus on/off, RADOS URLs on/off, sanitizer builds, Ceph/Gluster FSAL options, NFS protocol subsets, and packaging tests that verify generated paths and version strings.
