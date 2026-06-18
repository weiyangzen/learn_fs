# sources/storage-engines/foundationdb/contrib/SimpleOpt/CMakeLists.txt

Purpose: declares `contrib/SimpleOpt/include` as a CMake include directory for the vendored SimpleOpt single-header command-line parser.

Important APIs and control flow: the only command is `include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)`.

State and persistence: no build outputs are defined here; it mutates CMake include search state for consumers in the surrounding build.

Dependencies and integration: depends on the FoundationDB CMake hierarchy including this file before targets that include `SimpleOpt/SimpleOpt.h`.

Risks and test signals: directory-scoped include paths can unintentionally affect sibling targets. Build failures in C++ sources including `SimpleOpt/SimpleOpt.h` are the practical test signal.
