# sources/user-network-fs/nfs-ganesha/src/tools/multilock/CMakeLists.txt

Purpose: declares the multilock console and client tools used to drive file-locking scenarios across backends.

Important APIs, types, and functions: builds `ml_console`, `ml_posix_client`, optional `ml_cephfs_client`, and optional `ml_glusterfs_client`. Common sources are `ml_functions.c` and `multilock.h`.

Control flow: if `CEPH_FS_CEPH_STATX` is enabled, it sets `_FILE_OFFSET_BITS=64`, includes CephFS headers, builds `ml_cephfs_client`, and links CephFS libraries. If `USE_FSAL_GLUSTER AND USE_LKOWNER`, it includes GFAPI headers, builds `ml_glusterfs_client`, and links GFAPI libraries.

State and persistence: build graph only.

Dependencies and integration points: depends on math library, pthreads for clients, CephFS or GFAPI optional dependencies, and system libraries.

Risks: `add_definitions(-D_FILE_OFFSET_BITS=64)` applies directory-wide once CephFS statx is enabled. Optional client builds are tightly coupled to feature-detection variables and external library discovery.

Test signals: build matrix should cover base console/posix, CephFS-enabled, and Gluster/LKOWNER-enabled configurations.
