# sources/storage-engines/foundationdb/flow/bench/CMakeLists.txt

Purpose: defines the `flow_bench` executable target and its benchmark source files.

Important APIs/types/functions: CMake commands `add_executable`, `target_link_libraries`, and `target_include_directories`.

Control flow: target construction lists benchmark `.cpp` sources and the shared `BenchMain.cpp`. The target links against `flow`, Google Benchmark, and required platform libraries.

State/persistence: build-system metadata only; no runtime state.

Dependencies/integration: integrates Flow benchmark sources into the repository build. It also adds the local bench directory as an include path so files can include `BenchSupport.h`.

Risks: adding a new benchmark source requires updating this list or using a broader source collection elsewhere. Conditional library support such as zstd affects source behavior but this file still compiles the benchmark file.

Test signals: successful CMake generation/build of `flow_bench` and execution of benchmark filters validate the target.
