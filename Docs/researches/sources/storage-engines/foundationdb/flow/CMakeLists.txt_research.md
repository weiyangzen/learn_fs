# sources/storage-engines/foundationdb/flow/CMakeLists.txt

## Purpose
`flow/CMakeLists.txt` defines how the Flow library, tests, support tools, generated headers, optional compression, optional Swift support, and benchmarks are built.

## Important APIs, Types, and Functions
Important build constructs include `FLOW_USE_ZSTD`, `fdb_find_sources(FLOW_SRCS)`, `configure_file` for `ApiVersion.h`, `SourceVersion.h`, and `config.h`, protocol-version generation through `protocol_version.py`, `add_flow_target` for `flow`, `flow_sampling`, `flowlinktest`, and `flow_test`, and optional `flow_swift` targets.

## Control Flow
The script gathers sources, removes executable entry points from library sources, appends architecture-specific assembly, configures headers, ensures Python/Jinja2 availability for protocol generation, creates the Flow static libraries, links platform dependencies, and adds optional ZSTD and Swift wiring. It creates `flowlinktest` to force undefined symbol detection because static/shared library creation alone would not.

## State and Persistence Behavior
Build artifacts include generated headers under the binary include directory, generated Java/Python protocol files, optional virtualenv state for protocol generation, libraries, executables, and Swift interop headers. No runtime persistence is defined here.

## Dependencies and Integration Points
The file integrates with Threads, Python3, Jinja2, OpenSSL, Boost, fmt, crc32, libb64, stacktrace, coroutine detection, jemalloc, valgrind, platform libraries, zstd compilation, benchmarks, mkcert, acac, and Swift-to-C++ interop.

## Risks and Edge Cases
The fallback Jinja2 virtual environment modifies the build tree and depends on pip/ensurepip availability. Link libraries are accumulated in `FLOW_LIBS` inside a loop, so changes should avoid accidental duplication or leakage. Cross-compiling disables benchmarks and has Swift TODOs. Generated protocol and API files must be dependencies of all targets that include them.

## Test Signals
Build success of `flow`, `flow_sampling`, `flowlinktest`, and `flow_test` validates most wiring. `flowlinktest` is the explicit undefined-symbol gate, and optional feature paths are tested only when their CMake options are enabled.
