<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx98.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx98.hpp

## Purpose
This generated header validates a small set of C++98 standard-library facilities tracked by Boost.Config.

## Important APIs, Types, And Control Flow
It includes `boost/config.hpp` and emits `#error` if `BOOST_NO_CXX98_BINDERS`, `BOOST_NO_CXX98_FUNCTION_BASE`, or `BOOST_NO_CXX98_RANDOM_SHUFFLE` is defined. These correspond to older standard-library components that later standards deprecated or removed but Boost may still detect for compatibility.

## State And Persistence
The header has no runtime state, functions, or data. It only validates compile-time macro state.

## Dependencies And Integration Points
It depends on Boost.Config stdlib detection. It can be used by legacy compatibility checks that require C++98 library components.

## Risks And Test Signals
The main risk is using this as a gate in newer language modes where the standard library intentionally removed deprecated C++98 pieces. Test signals are compile checks under legacy language modes and targeted macro-injection failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx98.hpp -->
