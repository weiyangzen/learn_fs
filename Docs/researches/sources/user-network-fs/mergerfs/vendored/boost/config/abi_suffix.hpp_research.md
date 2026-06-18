<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi_suffix.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/abi_suffix.hpp

## Purpose
This wrapper ends a Boost ABI-controlled declaration region started by `boost/config/abi_prefix.hpp`.

## Important APIs, Types, And Control Flow
The header verifies `BOOST_CONFIG_ABI_PREFIX_HPP` is defined, otherwise emits an error because suffix use without prefix is invalid. It undefines that sentinel, includes `BOOST_ABI_SUFFIX` when ABI headers are enabled, and issues Borland warning-control cleanup when needed. It declares no functions or types.

## State And Persistence
It clears the prefix sentinel and pops compiler ABI state through the selected suffix header. No runtime state remains.

## Dependencies And Integration Points
It depends on `boost/config.hpp` having selected ABI headers and on a prior prefix include. It is paired with compiled Boost declaration blocks.

## Risks And Test Signals
Risk comes from unbalanced include structure: suffix without prefix is a hard compile error; prefix without suffix leaks packing/options. Test signals are negative compile tests for suffix-only inclusion and positive tests around class/struct declarations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi_suffix.hpp -->
