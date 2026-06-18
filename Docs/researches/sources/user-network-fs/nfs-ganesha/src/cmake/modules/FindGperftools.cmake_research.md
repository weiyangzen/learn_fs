# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindGperftools.cmake

Purpose: Finds gperftools profiler support.

Important APIs/types/functions: Consumes `Gperftools_ROOT_DIR`; finds `profiler` library into `GPERFTOOLS_PROFILER`, finds `gperftools/heap-profiler.h`, sets `GPERFTOOLS_LIBRARIES`, and uses `find_package_handle_standard_args`.

Control flow: Hinted library/header searches populate variables, then standard args report package status.

State and persistence behavior: CMake cache variables only.

Dependencies and integration points: Profiling or allocator-related build options can link the profiler library.

Risks: Comments mention tcmalloc but only profiler is searched. It does not find `tcmalloc` or `tcmalloc_and_profiler`, so allocator use is handled elsewhere or unsupported by this module.

Test signals: Configure with gperftools installed/missing, custom root, and profile-enabled target linking.
