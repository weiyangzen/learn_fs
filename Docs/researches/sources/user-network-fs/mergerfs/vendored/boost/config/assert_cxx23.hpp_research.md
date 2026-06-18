<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx23.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx23.hpp

## Purpose
This generated header validates selected C++23 standard-library header availability using Boost.Config.

## Important APIs, Types, And Control Flow
It includes `boost/config.hpp` and `boost/config/assert_cxx20.hpp`, then checks `BOOST_NO_CXX23_HDR_*` macros for `<expected>`, `<flat_map>`, `<flat_set>`, `<generator>`, `<mdspan>`, `<print>`, `<spanstream>`, `<stacktrace>`, and `<stdfloat>`. Any missing feature macro triggers an explanatory `#error`.

## State And Persistence
There is no runtime state. It is a compile-time feature assertion file.

## Dependencies And Integration Points
It depends on the full lower-standard assertion chain and up-to-date stdlib configuration. It should only be used in environments intending to require C++23 library coverage.

## Risks And Test Signals
C++23 support is still compiler/stdlib dependent, so this header is likely to fail on otherwise modern compilers. Test signals are compile-only checks under C++23 mode and per-header negative tests via `BOOST_NO_CXX23_HDR_*` definitions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx23.hpp -->
