<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler.h` is a umbrella compiler include that detects known compiler front ends and emulated compilers in a precedence-sensitive order. It is an aggregation header: its job is to include the concrete detector headers in a stable order rather than to perform substantial detection itself.

## Important APIs, Types, and Functions

The header exports the macros provided by its direct includes. Direct includes are `boost/predef/compiler/borland.h`, `boost/predef/compiler/clang.h`, `boost/predef/compiler/comeau.h`, `boost/predef/compiler/compaq.h`, `boost/predef/compiler/diab.h`, `boost/predef/compiler/digitalmars.h`, `boost/predef/compiler/dignus.h`, `boost/predef/compiler/edg.h`, `boost/predef/compiler/ekopath.h`, `boost/predef/compiler/gcc_xml.h`, `boost/predef/compiler/gcc.h`, `boost/predef/compiler/greenhills.h`, `boost/predef/compiler/hp_acc.h`, `boost/predef/compiler/iar.h`, `boost/predef/compiler/ibm.h`, `boost/predef/compiler/intel.h`, `boost/predef/compiler/kai.h`, `boost/predef/compiler/llvm.h`, `boost/predef/compiler/metaware.h`, `boost/predef/compiler/metrowerks.h`, `boost/predef/compiler/microtec.h`, `boost/predef/compiler/mpw.h`, `boost/predef/compiler/nvcc.h`, `boost/predef/compiler/palm.h`, `boost/predef/compiler/pgi.h`, `boost/predef/compiler/sgi_mipspro.h`, `boost/predef/compiler/sunpro.h`, `boost/predef/compiler/tendra.h`, `boost/predef/compiler/visualc.h`, `boost/predef/compiler/watcom.h`. Consumers normally include this file when they want the whole `compiler.h` detection family instead of selecting an individual detector.

## Control Flow

Preprocessor control flow is include-driven. The include guard prevents repeated expansion, then each listed child header runs its own detection logic, defines a `BOOST_*` version macro, optionally defines an `*_AVAILABLE` marker, and registers Boost.Predef tests.

## State and Persistence Behavior

There is no runtime state or persistence. The only state is the set of preprocessor macros produced during translation of the including source file.

## Dependencies and Integration Points

This header is part of the vendored Boost.Predef tree consumed by mergerfs through vendored Boost headers. It integrates by making platform/compiler/OS facts available to conditional compilation paths without requiring external Boost installation.

## Risks and Edge Cases

Aggregation order matters for detectors that emulate another compiler or operating system. Removing or reordering includes can change which macro becomes primary. Because this is vendored code, partial updates can leave an umbrella header pointing at missing or incompatible child headers.

## Test Signals

Compile a small translation unit that includes `sources/user-network-fs/mergerfs/vendored/boost/predef/compiler.h` and checks expected `BOOST_*` macros under representative host toolchains. The Boost.Predef `BOOST_PREDEF_DECLARE_TEST` registrations in child headers are also useful upstream signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler.h -->
