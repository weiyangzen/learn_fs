<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx20.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx20.hpp

## Purpose
This generated header validates C++20 library/header coverage according to Boost.Config.

## Important APIs, Types, And Control Flow
It includes `boost/config.hpp` and `boost/config/assert_cxx17.hpp`, then errors for missing `BOOST_NO_CXX20_HDR_*` macros. Checked headers include `<barrier>`, `<bit>`, `<compare>`, `<concepts>`, `<coroutine>`, `<format>`, `<latch>`, `<numbers>`, `<ranges>`, `<semaphore>`, `<source_location>`, `<span>`, `<stop_token>`, `<syncstream>`, and `<version>`.

## State And Persistence
The header has no runtime state. It acts entirely through compile-time errors.

## Dependencies And Integration Points
It depends on all lower standard assertion headers and Boost.Config stdlib detection. It is a strict feature gate before relying on C++20 standard-library facilities.

## Risks And Test Signals
Risks are high because C++20 library support is uneven across compiler/stdlib combinations; `<format>`, `<ranges>`, and coroutine headers are common fault lines. Test signals are CI compile tests under C++20 mode on each supported toolchain and negative tests defining one `BOOST_NO_CXX20_HDR_*` macro at a time.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx20.hpp -->
