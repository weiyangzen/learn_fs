# sources/storage-engines/wiredtiger/test/model/CMakeLists.txt

Purpose: defines the shared `wiredtiger_model` C++17 library and pulls in model tests and tools.

Important behavior: `add_library(wiredtiger_model SHARED ...)` compiles core model files, driver parsers/generators/runners, and verification code. `target_include_directories` exposes `src/include` publicly and adds build config, WiredTiger source includes, and test third-party includes privately. Compile options require `-std=c++17` and `-Wnon-virtual-dtor`. The library links `Iconv::Iconv`, dynamic loading libraries, and `wt::wiredtiger`. It then adds `test` and `tools` subdirectories.

Control flow and state: build metadata only; no runtime state. The duplicate `target_include_directories` block is redundant but harmless.

Dependencies and integration: integrates with nlohmann JSON in third-party includes, WiredTiger internal/public headers, iconv for UTF-8 decoding, dlopen support for library path discovery, and the WiredTiger target.

Risks and test signals: shared-library linkage and private internal headers mean ABI/build layout changes can break model tooling. Iconv availability is required. The model tests/tools provide validation that all listed sources compile and link as a coherent testing library.
