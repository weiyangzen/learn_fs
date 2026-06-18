<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/CMakeLists.txt

## Purpose
Builds the MainNFSD object library and shared `ganesha_nfsd` library, selecting feature-gated daemon, FSAL, callback, 9P, RDMA, QOS, monitoring, DBus, and protocol components.

## Important APIs, Types, And Functions
- `MainServices_STAT_SRCS` lists core service sources.
- `add_library(MainServices OBJECT ...)` compiles service objects as PIC.
- `fsal_CORE_SRCS` includes FSAL core and `FSAL_UP/fsal_up_top.c`.
- `ganesha_nfsd_OBJS` aggregates dependent object libraries.
- Conditional blocks control DBus, NLM, RQUOTA, NFSACL, 9P, RDMA, QOS, callback simulators, monitoring, and LTTng.

## Control Flow
CMake sets definitions/includes, builds `MainServices`, defines FSAL core sources, creates shared `ganesha_nfsd`, links TIRPC/system/LTTng/Mooshika/monitoring/trace libraries, applies undefined-symbol and version-script flags, sets version/SOVERSION, and installs the library.

## State And Persistence Behavior
Controls build artifacts, linked features, sanitizer instrumentation, symbol visibility, and install output. Runtime feature availability follows these selections.

## Dependencies And Integration Points
Integrates MainNFSD with FSAL, SAL, protocol, callback, MDCACHE, monitoring, DBus, Mooshika, nTIRPC, and LTTng object/link dependencies.

## Risks
- `nfs_rpc_callback_simulator.c` is appended twice under `USE_CB_SIMULATOR`.
- Mooshika libraries are listed globally even though RDMA sources are conditional.
- Version-script and undefined-symbol behavior differs by platform/ASAN.
- Directly compiling `fsal_up_top.c` into `ganesha_nfsd` affects all users of the top upcall vector.

## Test Signals
Build feature matrices for default, 9P, RDMA, DBus, QOS, monitoring, ASAN, and LTTng; inspect duplicate source warnings and shared-library exported symbols.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/CMakeLists.txt -->
