<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/borland.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/borland.hpp

## Purpose
This Boost.Config compiler adapter describes classic Borland C++ capabilities and defects.

## Important APIs, Types, And Control Flow
It rejects unsupported compiler versions, classifies the bundled stdlib as Rogue Wave, STLport, or Dinkumware, and defines many `BOOST_NO_*` macros for known defects: member template friends, cv specializations, SFINAE, template templates, complete value initialization, int64 limitations, two-phase lookup, nested friendship, and broad C++11 feature gaps. It defines positives such as `BOOST_HAS_LONG_LONG`, `BOOST_HAS_STDINT_H`, `BOOST_HAS_MS_INT64`, `BOOST_HAS_DIRENT_H`, and ABI header paths when available.

## State And Persistence
All state is preprocessor state. It may include standard headers to patch missing constants or broken declarations, but no runtime objects are created.

## Dependencies And Integration Points
It is selected by Boost.Config compiler detection. It integrates with ABI wrappers through Borland prefix/suffix headers and with platform config by defining `BOOST_DISABLE_WIN32` under strict ANSI modes.

## Risks And Test Signals
Risks include stale version ranges, forced `#error` for newer versions, broad defect macros disabling usable features, and ABI pragma dependence. Test signals are Boost.Config check-suite compilation on each Borland version, especially exception handling, stdint, ABI prefix/suffix, and C++11 feature gates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/borland.hpp -->
