# sources/security-integrity/cryfs/old-cpp/src/fspp/fuse/CMakeLists.txt

Purpose: CMake build definition for the static `fspp-fuse` adapter library.

Important APIs/types/functions: CMake target `fspp-fuse`, sources `FilesystemImpl.cpp`, `Profiler.cpp`, `Fuse.cpp`, compile definition `_FILE_OFFSET_BITS=64`, Boost helper macros, Dokan configuration, and `PkgConfig::Fuse`.

Control flow: always builds a static library and links `cpp-utils` plus `fspp-interface`. On Windows it locates Dokan by architecture and installs required DLLs; on Linux/macOS it requires pkg-config and FUSE.

State and persistence behavior: no runtime state, but `_FILE_OFFSET_BITS=64` affects ABI and large-file stat behavior for all consumers of the target.

Dependencies and integration points: integrates with platform FUSE/Dokan libraries, CMake helper functions, Boost, and the fspp interface target.

Risks and test signals: architecture branch hard-fails unsupported Windows targets. FUSE dependency is mandatory outside Windows. macOS sets `CMAKE_FIND_FRAMEWORK LAST` after FUSE setup, which may affect dependency resolution globally in this directory scope.
