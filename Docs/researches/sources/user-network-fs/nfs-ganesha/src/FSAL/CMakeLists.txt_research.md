<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/CMakeLists.txt

Purpose: FSAL dispatcher CMake file. It adds the common stackable and pseudo FSAL directories unconditionally and gates backend FSAL subdirectories according to top-level feature options.

Important APIs, types, and functions: Uses `add_subdirectory` only. Unconditional directories are `Stackable_FSALs` and `FSAL_PSEUDO`. Conditional directories include `FSAL_VFS` for any of `USE_FSAL_VFS`, `USE_FSAL_LUSTRE`, or `USE_FSAL_XFS`, plus `FSAL_PROXY_V4`, `FSAL_PROXY_V3`, `FSAL_CEPH`, `FSAL_RGW`, `FSAL_SAUNAFS`, `FSAL_GPFS`, `FSAL_GLUSTER`, `FSAL_LIZARDFS`, `FSAL_KVSFS`, and `FSAL_MEM`.

Control flow: CMake enters this file after the root script has already validated dependencies and normalized feature flags. Each `if(USE_FSAL_*)` block adds the matching backend directory. The VFS directory is shared by VFS, Lustre, and XFS support, so any of those options pulls in that subtree.

State and persistence behavior: This file creates no generated files or cache state. Its effect is build graph composition: which FSAL module targets and sources become visible to the build.

Dependencies and integration points: Depends entirely on options defined in the top-level `CMakeLists.txt`. It is the bridge from global dependency detection to backend-specific CMake files such as `FSAL/FSAL_CEPH/CMakeLists.txt`. Runtime FSAL availability follows from whether these module targets were built and installed.

Risks: Mis-set top-level options can omit an FSAL silently at this layer. The shared VFS/Lustre/XFS condition means maintainers must understand that disabling `USE_FSAL_VFS` alone does not necessarily exclude `FSAL_VFS` if Lustre or XFS remains enabled. There is no local validation here, so backend prerequisites must stay correct in the root script.

Test signals: Configure with selected FSAL toggles and inspect generated targets or the configure summary. A Ceph-enabled configure should enter `FSAL_CEPH`; a Ceph-disabled configure should not create the `fsalceph` module target.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/CMakeLists.txt -->
