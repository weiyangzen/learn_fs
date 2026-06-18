# sources/storage-engines/wiredtiger/tools/memory-model-test/CMakeLists.txt

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/memory-model-test/CMakeLists.txt -->
## sources/storage-engines/wiredtiger/tools/memory-model-test/CMakeLists.txt

### Purpose
This CMake file builds the standalone `memory_model_test` executable used to demonstrate and stress memory-ordering behavior on x86 and ARM64.

### Important APIs, Types, and Functions
It requires CMake 3.21, sets C++20, prefers pthreads, finds `Threads`, builds `memory_model_test` from `memory_model_test.cpp` and `basic_semaphore.h`, links `Threads::Threads`, and compiles with `-O2 -Wall -Werror`.

### Control Flow
Configuration is linear: project declaration, language standard, thread package discovery, executable creation, link, and compile options.

### State and Persistence
No runtime state is managed by CMake. Build artifacts are local to the build tree.

### Dependencies and Integration Points
Requires a C++20-capable compiler unless `AVOID_CPP20_SEMAPHORE` is passed to the source build. The target links platform thread support.

### Risks and Test Signals
`-Werror` can break builds on compiler-version warning changes. The source has architecture-specific barrier definitions only for x86_64 and aarch64, so other architectures may fail. Test signals are successful configure/build and smoke runs with small `-n` iteration counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/memory-model-test/CMakeLists.txt -->
