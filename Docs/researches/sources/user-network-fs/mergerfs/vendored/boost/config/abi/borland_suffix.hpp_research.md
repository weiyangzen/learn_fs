<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi/borland_suffix.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/abi/borland_suffix.hpp

## Purpose
This header is the matching suffix for Borland ABI configuration. It restores compiler option state after Boost declarations that were wrapped by `borland_prefix.hpp`.

## Important APIs, Types, And Control Flow
The entire operational body is `#pragma option pop` followed by `#pragma nopushoptwarn`. There are no exported macros, types, or functions beyond compiler pragma effects.

## State And Persistence
It unwinds compiler option state previously pushed by the prefix. After inclusion, no runtime state or persistent file output remains.

## Dependencies And Integration Points
It is referenced by `BOOST_ABI_SUFFIX` and included indirectly by `boost/config/abi_suffix.hpp`. It must be paired with `borland_prefix.hpp` in the same declaration region.

## Risks And Test Signals
Risk is structural: missing the suffix leaves changed ABI options active for later user code; using the suffix without a prefix can pop unrelated compiler state. Test signals are preprocessor/include-balance tests and compilation of Boost declarations surrounded by `abi_prefix.hpp`/`abi_suffix.hpp` on Borland-family compilers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi/borland_suffix.hpp -->
