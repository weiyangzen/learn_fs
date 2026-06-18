# sources/distributed-fs/xrootd/src/XrdCeph/CMakeLists.txt

Purpose: defines conditional Ceph support targets, including the Ceph POSIX helper library, main XrdCeph OSS plugin, and xattr plugin.

Important APIs/types/functions: checks `ENABLE_CEPH`, `FORCE_ENABLED`, and `find_package(ceph)`; sets `BUILD_CEPH`; builds `XrdCephPosix`, module `XrdCeph-${PLUGIN_VERSION}`, and module `XrdCephXattr-${PLUGIN_VERSION}`; links `RADOS_LIBS`, `XrdUtils`, and `XrdServer`; exports RADOS include paths.

Control flow: if Ceph is disabled or unavailable without force, it unsets `BUILD_CEPH` and returns. Otherwise targets are declared and installed.

State and persistence: build-system state only. Runtime persistence is in Ceph/RADOS and plugin behavior outside this file.

Dependencies and integration points: integrates librados/ceph detection with XRootD plugin modules. The buffer sources researched here are part of the main XrdCeph module.

Risks: build behavior changes substantially with `FORCE_ENABLED`; missing Ceph packages disable plugin silently unless forced. The buffer code is compiled only when the main module builds, so standalone tests need matching include/link setup.

Test signals: configure with Ceph disabled, optional missing, forced missing, and present; verify target names, link libraries, include dirs, SOVERSION for `XrdCephPosix`, and installed modules.
