# sources/storage-engines/foundationdb/contrib/rapidxml/CMakeLists.txt

## Purpose

This CMake file declares RapidXML as a header-only interface library for the FoundationDB source tree. It gives consumers a target they can link against to inherit the RapidXML include directory.

## Important APIs and Types

The build API is the `rapidxml` CMake target created with `add_library(rapidxml INTERFACE)`. `target_include_directories(rapidxml INTERFACE "${CMAKE_CURRENT_SOURCE_DIR}/include")` publishes the local `include` directory to target consumers.

## Control Flow

Configuration simply registers the interface target and attaches include usage requirements. No source files are compiled and no install/export rules are defined here.

## State and Persistence

There is no runtime state. Build-system state is limited to the CMake target and its include path property during configure/generate.

## Dependencies and Integration Points

Any FoundationDB target that links to `rapidxml` receives the RapidXML headers on its include path. The file assumes the vendored RapidXML headers live under `contrib/rapidxml/include` relative to this CMake file.

## Risks and Edge Cases

Because the target is header-only, consumers rely on transitive include propagation and compiler settings from their own targets. The file does not guard against duplicate target names, does not define version metadata, and does not expose system include semantics. A moved or missing `include` directory would only surface when a dependent target compiles.

## Test Signals

Build validation should configure the FoundationDB tree, link at least one consumer against `rapidxml`, and compile a translation unit that includes a RapidXML header through the target's propagated include directory.
