<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi/borland_prefix.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/abi/borland_prefix.hpp

## Purpose
This ABI prefix header normalizes Borland/C++Builder compiler options around Boost declarations so separately compiled Boost binaries and consuming code use compatible structure layout, enum sizing, calling convention, member pointer layout, and name mangling.

## Important APIs, Types, And Control Flow
The file emits Borland pragmas: `#pragma nopushoptwarn` and `#pragma option push -a8 -Vx- -Ve- -b- -pc -Vmv -VC- -Vl- -w-8027 -w-8026`. It pushes the current option state and applies the ABI settings Boost expects. There are no C++ declarations or runtime control paths.

## State And Persistence
The state is compiler option state on the include stack. It persists only until the matching Borland suffix header pops the options.

## Dependencies And Integration Points
It is selected through `BOOST_ABI_PREFIX` by Borland/CodeGear compiler config headers and included by `boost/config/abi_prefix.hpp` when `BOOST_HAS_ABI_HEADERS` is active.

## Risks And Test Signals
Risks are unmatched prefix/suffix includes, accidental use outside Borland-family compilers, and ABI mismatch if user code changes the same options around Boost headers. Test signals are compile-only ABI-header balance tests and binary compatibility checks for compiled Boost libraries under C++Builder.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi/borland_prefix.hpp -->
