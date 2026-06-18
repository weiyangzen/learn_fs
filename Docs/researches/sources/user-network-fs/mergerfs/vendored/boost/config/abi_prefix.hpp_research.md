<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi_prefix.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/abi_prefix.hpp

## Purpose
This wrapper begins a Boost ABI-controlled declaration region. It enforces single active prefix inclusion and delegates to the compiler-selected ABI prefix header when available.

## Important APIs, Types, And Control Flow
The header defines `BOOST_CONFIG_ABI_PREFIX_HPP` and errors on double inclusion. It includes `boost/config.hpp`, then includes `BOOST_ABI_PREFIX` when `BOOST_HAS_ABI_HEADERS` is defined. For Borland it also emits `#pragma nopushoptwarn`. It declares no runtime APIs.

## State And Persistence
The persistent state is a preprocessor sentinel indicating that an ABI prefix is active, plus any compiler pragma state pushed by the selected ABI header. The state must be released by `abi_suffix.hpp`.

## Dependencies And Integration Points
It depends on `boost/config.hpp` to choose compiler ABI headers. Boost compiled library headers include it after all other includes and before declarations whose binary ABI must match shipped libraries.

## Risks And Test Signals
Risks are double inclusion, forgetting `abi_suffix.hpp`, or including code before the prefix. Test signals include intentional double-prefix compile failures, balanced prefix/suffix compile tests, and ABI checks with MSVC/Borland configs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi_prefix.hpp -->
