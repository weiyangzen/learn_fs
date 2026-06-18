<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi/msvc_prefix.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/abi/msvc_prefix.hpp

## Purpose
This ABI prefix header forces MSVC packing for compiled Boost declarations to match Boost binary layout regardless of project-level packing settings.

## Important APIs, Types, And Control Flow
The header checks `_M_X64`: on x64 it emits `#pragma pack(push,16)`, otherwise `#pragma pack(push,8)`. No declarations or functions are introduced. The paired suffix restores the prior packing.

## State And Persistence
The only state is compiler packing state. It persists across following declarations until `msvc_suffix.hpp` pops it.

## Dependencies And Integration Points
It is selected by MSVC compiler config through `BOOST_ABI_PREFIX` and reached via `boost/config/abi_prefix.hpp` for Boost libraries with separately compiled components. Header-only code generally does not need it when all translation units share compiler options.

## Risks And Test Signals
Risks include unbalanced include pairs, mixed pack settings around exported structs/classes, and ABI mismatch when separately built Boost binaries do not match consumer layout. Test signals include pack-balance compile tests, x86 vs x64 object layout checks, and builds with user project packing overridden before including Boost headers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/abi/msvc_prefix.hpp -->
