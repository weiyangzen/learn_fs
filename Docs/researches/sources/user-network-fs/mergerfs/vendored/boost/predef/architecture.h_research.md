<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture.h` is a umbrella architecture include that gathers all CPU architecture predefs and exposes their available/version macros to callers. It is an aggregation header: its job is to include the concrete detector headers in a stable order rather than to perform substantial detection itself.

## Important APIs, Types, and Functions

The header exports the macros provided by its direct includes. Direct includes are `boost/predef/architecture/alpha.h`, `boost/predef/architecture/arm.h`, `boost/predef/architecture/blackfin.h`, `boost/predef/architecture/convex.h`, `boost/predef/architecture/e2k.h`, `boost/predef/architecture/ia64.h`, `boost/predef/architecture/loongarch.h`, `boost/predef/architecture/m68k.h`, `boost/predef/architecture/mips.h`, `boost/predef/architecture/parisc.h`, `boost/predef/architecture/ppc.h`, `boost/predef/architecture/ptx.h`, `boost/predef/architecture/pyramid.h`, `boost/predef/architecture/riscv.h`, `boost/predef/architecture/rs6k.h`, `boost/predef/architecture/sparc.h`, `boost/predef/architecture/superh.h`, `boost/predef/architecture/sys370.h`, `boost/predef/architecture/sys390.h`, `boost/predef/architecture/x86.h`, `boost/predef/architecture/z.h`. Consumers normally include this file when they want the whole `architecture.h` detection family instead of selecting an individual detector.

## Control Flow

Preprocessor control flow is include-driven. The include guard prevents repeated expansion, then each listed child header runs its own detection logic, defines a `BOOST_*` version macro, optionally defines an `*_AVAILABLE` marker, and registers Boost.Predef tests.

## State and Persistence Behavior

There is no runtime state or persistence. The only state is the set of preprocessor macros produced during translation of the including source file.

## Dependencies and Integration Points

This header is part of the vendored Boost.Predef tree consumed by mergerfs through vendored Boost headers. It integrates by making platform/compiler/OS facts available to conditional compilation paths without requiring external Boost installation.

## Risks and Edge Cases

Aggregation order matters for detectors that emulate another compiler or operating system. Removing or reordering includes can change which macro becomes primary. Because this is vendored code, partial updates can leave an umbrella header pointing at missing or incompatible child headers.

## Test Signals

Compile a small translation unit that includes `sources/user-network-fs/mergerfs/vendored/boost/predef/architecture.h` and checks expected `BOOST_*` macros under representative host toolchains. The Boost.Predef `BOOST_PREDEF_DECLARE_TEST` registrations in child headers are also useful upstream signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture.h -->
