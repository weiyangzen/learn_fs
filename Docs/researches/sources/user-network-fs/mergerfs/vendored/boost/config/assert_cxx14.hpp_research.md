<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx14.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx14.hpp

## Purpose
This generated header validates C++14 support according to Boost.Config.

## Important APIs, Types, And Control Flow
It includes `boost/config.hpp` and `boost/config/assert_cxx11.hpp`, then errors if C++14 defect macros are present. Checked features include aggregate NSDMI, binary literals, relaxed `constexpr`, `decltype(auto)`, digit separators, generic lambdas, `<shared_mutex>`, initialized lambda captures, return type deduction, `std::exchange`, and variable templates.

## State And Persistence
The header has no runtime behavior. It either preprocesses cleanly or halts compilation with an explanatory `#error`.

## Dependencies And Integration Points
It depends on C++11 validation passing first and on Boost.Config's compiler/stdlib feature probes. It can be included by tests or build configuration checks before enabling code paths that rely on C++14.

## Risks And Test Signals
Risks include standard-library feature lag even when the compiler language mode is C++14, especially `<shared_mutex>` and `std::exchange`. Test signals include compiling under `-std=c++14`/equivalent and injected `BOOST_NO_CXX14_*` macros to verify failures are specific.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx14.hpp -->
