<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/std.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/std.h` is a umbrella C++ standard-library include that includes the stdlib prefix and known implementation detectors. It is an aggregation header: its job is to include the concrete detector headers in a stable order rather than to perform substantial detection itself.

## Important APIs, Types, and Functions

The header exports the macros provided by its direct includes. Direct includes are `boost/predef/library/std/_prefix.h`, `boost/predef/library/std/cxx.h`, `boost/predef/library/std/dinkumware.h`, `boost/predef/library/std/libcomo.h`, `boost/predef/library/std/modena.h`, `boost/predef/library/std/msl.h`, `boost/predef/library/std/msvc.h`, `boost/predef/library/std/roguewave.h`, `boost/predef/library/std/sgi.h`, `boost/predef/library/std/stdcpp3.h`, `boost/predef/library/std/stlport.h`, `boost/predef/library/std/vacpp.h`. Consumers normally include this file when they want the whole `library/std.h` detection family instead of selecting an individual detector.

## Control Flow

Preprocessor control flow is include-driven. The include guard prevents repeated expansion, then each listed child header runs its own detection logic, defines a `BOOST_*` version macro, optionally defines an `*_AVAILABLE` marker, and registers Boost.Predef tests.

## State and Persistence Behavior

There is no runtime state or persistence. The only state is the set of preprocessor macros produced during translation of the including source file.

## Dependencies and Integration Points

This header is part of the vendored Boost.Predef tree consumed by mergerfs through vendored Boost headers. It integrates by making platform/compiler/OS facts available to conditional compilation paths without requiring external Boost installation.

## Risks and Edge Cases

Aggregation order matters for detectors that emulate another compiler or operating system. Removing or reordering includes can change which macro becomes primary. Because this is vendored code, partial updates can leave an umbrella header pointing at missing or incompatible child headers.

## Test Signals

Compile a small translation unit that includes `sources/user-network-fs/mergerfs/vendored/boost/predef/library/std.h` and checks expected `BOOST_*` macros under representative host toolchains. The Boost.Predef `BOOST_PREDEF_DECLARE_TEST` registrations in child headers are also useful upstream signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std.h -->
