# sources/distributed-fs/xrootd/src/XrdXml/CMakeLists.txt

## Purpose

This CMake file builds the `XrdXml` shared library and wires in the bundled TinyXML object library plus optional libxml2-backed reader support.

## Important APIs, Types, and Functions

- `add_subdirectory(tinyxml)`: builds `XrdTinyXml` from the bundled TinyXML source.
- `add_library(XrdXml SHARED ...)`: includes metalink conversion, TinyXML reader, and abstract reader sources.
- `find_package(LibXml2)`: conditionally adds `XrdXmlRdrXml2.cc/.hh`, defines `HAVE_XML2`, and links `LibXml2::LibXml2`.
- `target_link_libraries(XrdXml PUBLIC XrdTinyXml PRIVATE XrdUtils ${CMAKE_THREAD_LIBS_INIT})`: exposes the TinyXML object dependency and private XRootD utility/thread dependencies.

## Control Flow

The build always includes the TinyXML adapter and abstract XML reader. If libxml2 is found at configure time, the streaming XML reader is compiled into the same shared library and made selectable at runtime by `XrdXmlReader::GetReader(..., "libxml2")`.

## State and Persistence Behavior

No runtime state is kept here. The file controls shared object version metadata using `${XRootD_VERSION_MAJOR}` and `${XRootD_LIBVERSION}` and installs the resulting library into `${CMAKE_INSTALL_LIBDIR}`.

## Dependencies and Integration Points

`XrdXml` integrates with `XrdTinyXml`, `XrdUtils`, thread libraries, and optional LibXml2. The `HAVE_XML2` compile definition is consumed by `XrdXmlReader.cc` to expose the libxml2 implementation.

## Risks

- Runtime support for `"libxml2"` silently depends on configure-time discovery; code using that implementation must handle `ENOTSUP`.
- `XrdTinyXml` is public, so include path and object-library details can affect downstream targets.
- The bundled TinyXML code is old and receives no external package update through this CMake path.

## Test Signals

Build tests should cover configurations with and without LibXml2, verify that `XrdXml` links and installs with the expected SO version, and check that `XrdXmlReader::Init("libxml2")` behaves according to `LIBXML2_FOUND`.
