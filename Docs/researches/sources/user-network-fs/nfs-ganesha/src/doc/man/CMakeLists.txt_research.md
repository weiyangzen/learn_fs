<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/doc/man/CMakeLists.txt -->
## sources/user-network-fs/nfs-ganesha/src/doc/man/CMakeLists.txt

Purpose: generates and installs NFS-Ganesha man pages from reStructuredText using Sphinx.

Important build surface: initializes core man sources (`ganesha-config`, log, cache, export, core) and conditionally appends pages based on feature options such as `USE_9P`, `USE_FSAL_CEPH`, `USE_FSAL_RGW`, `USE_FSAL_XFS`, `USE_FSAL_GLUSTER`, `USE_FSAL_VFS`, `ENABLE_QOS`, `USE_FSAL_LUSTRE`, `USE_FSAL_PROXY_V4`, `USE_FSAL_PROXY_V3`, `USE_FSAL_GPFS`, and `USE_RADOS_RECOV`. It creates output paths under `${CMAKE_BINARY_DIR}/doc`, installs `.8` files to `share/man/man8`, and defines `manpages ALL`.

Control flow/state: CMake expands the source list, registers one Sphinx custom command producing all selected man outputs, and makes the always-built `manpages` target depend on them.

Dependencies/integration: requires `${SPHINX_BUILD}` and `conf.py`. Feature flags align generated documentation with compiled FSAL/protocol support.

Risks: installing files declared as custom-command outputs can be fragile if Sphinx fails or source lists diverge from `conf.py`. Because `manpages` is `ALL`, missing Sphinx breaks normal builds when `USE_MAN_PAGE` is enabled.

Test signals: run a build with representative FSAL flags and verify generated `.8` files match selected `.rst` inputs and install into the expected man8 directory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/doc/man/CMakeLists.txt -->
