# sources/storage-engines/rocksdb/cmake/modules/CxxFlags.cmake

## Purpose
Defines one macro, `get_cxx_std_flags`, to recover the compiler flag associated with the current `CMAKE_CXX_STANDARD` and whether strict standard mode is required.

## Important APIs and Control Flow
`get_cxx_std_flags(FLAGS_VARIABLE)` sets the caller-provided variable to either `CMAKE_CXX${CMAKE_CXX_STANDARD}_STANDARD_COMPILE_OPTION` when `CMAKE_CXX_STANDARD_REQUIRED` is true, or to `CMAKE_CXX${CMAKE_CXX_STANDARD}_EXTENSION_COMPILE_OPTION` otherwise. This mirrors CMake's internal standard flag selection but exposes the selected flag for RocksDB build logic.

## Dependencies, Risks, and Test Signals
It relies on CMake-populated standard option variables and caller configuration of `CMAKE_CXX_STANDARD`. There is no persistence. The main risk is empty output if CMake does not define the chosen standard option for the active compiler/generator, or if `CMAKE_CXX_STANDARD` is unset. Test signal is build-system configuration coverage across compilers.
