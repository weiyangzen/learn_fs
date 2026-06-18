# sources/distributed-fs/xrootd/src/XrdXml/tinyxml/CMakeLists.txt

## Purpose

This CMake file builds the bundled TinyXML source as the `XrdTinyXml` object library used by `XrdXml`.

## Important APIs, Types, and Functions

- `add_library(XrdTinyXml OBJECT ...)`: compiles `tinystr`, `tinyxml`, error text, and parser sources into reusable object files.
- `POSITION_INDEPENDENT_CODE ON`: makes objects safe to include in shared libraries.
- `target_include_directories(... PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>)`: exposes `tinyxml.h` and `tinystr.h` during the build.

## Control Flow

The parent `XrdXml` CMake file adds this subdirectory, then links the object library into the shared `XrdXml` library.

## State and Persistence Behavior

No runtime state exists here. It controls build-time object composition and include paths only.

## Dependencies and Integration Points

The object library is the dependency that lets `XrdXmlRdrTiny.cc` include `tinyxml.h` without a system TinyXML package.

## Risks

- Object library consumers inherit bundled TinyXML implementation details.
- There is no versioned external package boundary; updating TinyXML means editing vendored source.
- Public include exposure can collide if another target also uses a different TinyXML header.

## Test Signals

Build tests should verify position-independent compilation and that `XrdXmlRdrTiny.cc` can include `tinyxml.h` via the target include path.
