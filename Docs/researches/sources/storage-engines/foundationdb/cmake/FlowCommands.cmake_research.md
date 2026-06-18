# sources/storage-engines/foundationdb/cmake/FlowCommands.cmake

## Purpose
Defines the core FoundationDB target-building DSL for Flow/C++ sources, actor compilation, coverage XML, header copying, and stripped package binaries.

## Important APIs, Types, and Functions
Defines target properties `SOURCE_FILES` and `COVERAGE_FILTERS`, `generate_coverage_xml`, `strip_debug_symbols`, `copy_headers`, and `add_flow_target`.

## Control Flow and Integration
`add_flow_target` expands `.actor.*` inputs into generated `.actor.g.*` files using actor compiler commands, creates executable/static/dynamic/link-test targets, wires fdboptions dependencies, marks generated files, emits coverage targets, and creates strip/debug-symbol package targets. It also passes `COMPILATION_UNIT` compile definitions when enabled.

## State and Persistence
Depends on `ACTORCOMPILER_COMMAND`, `coveragetool_command`, `fdboptions`, CMake target properties, platform strip/objcopy tools, and helper functions from `utils.cmake`.

## Dependencies
State is extensive: generated actor files, custom targets, target properties, package-stripped binaries under `packages/bin` or `packages/lib`, and coverage XML files.

## Risks and Test Signals
Risks include generated-file dependency mistakes, broad global output directory changes for link tests, coverage filter property mismatch, and platform strip behavior. Test signals are successful actor generation, target builds, coverage XML, and package stripped artifacts.
