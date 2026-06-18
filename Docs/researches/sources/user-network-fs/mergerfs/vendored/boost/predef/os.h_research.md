<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/os.h` is a umbrella operating-system include that aggregates AIX, AmigaOS, BeOS, BSD family, Cygwin, Haiku, HP-UX, IRIX, iOS, Linux, macOS, OS/400, QNX, Solaris, Unix, VMS, and Windows detectors. It is an aggregation header: its job is to include the concrete detector headers in a stable order rather than to perform substantial detection itself.

## Important APIs, Types, and Functions

The header exports the macros provided by its direct includes. Direct includes are `boost/predef/os/aix.h`, `boost/predef/os/amigaos.h`, `boost/predef/os/beos.h`, `boost/predef/os/bsd.h`, `boost/predef/os/cygwin.h`, `boost/predef/os/haiku.h`, `boost/predef/os/hpux.h`, `boost/predef/os/irix.h`, `boost/predef/os/ios.h`, `boost/predef/os/linux.h`, `boost/predef/os/macos.h`, `boost/predef/os/os400.h`, `boost/predef/os/qnxnto.h`, `boost/predef/os/solaris.h`, `boost/predef/os/unix.h`, `boost/predef/os/vms.h`, `boost/predef/os/windows.h`. Consumers normally include this file when they want the whole `os.h` detection family instead of selecting an individual detector.

## Control Flow

Preprocessor control flow is include-driven. The include guard prevents repeated expansion, then each listed child header runs its own detection logic, defines a `BOOST_*` version macro, optionally defines an `*_AVAILABLE` marker, and registers Boost.Predef tests.

## State and Persistence Behavior

There is no runtime state or persistence. The only state is the set of preprocessor macros produced during translation of the including source file.

## Dependencies and Integration Points

This header is part of the vendored Boost.Predef tree consumed by mergerfs through vendored Boost headers. It integrates by making platform/compiler/OS facts available to conditional compilation paths without requiring external Boost installation.

## Risks and Edge Cases

Aggregation order matters for detectors that emulate another compiler or operating system. Removing or reordering includes can change which macro becomes primary. Because this is vendored code, partial updates can leave an umbrella header pointing at missing or incompatible child headers.

## Test Signals

Compile a small translation unit that includes `sources/user-network-fs/mergerfs/vendored/boost/predef/os.h` and checks expected `BOOST_*` macros under representative host toolchains. The Boost.Predef `BOOST_PREDEF_DECLARE_TEST` registrations in child headers are also useful upstream signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os.h -->
