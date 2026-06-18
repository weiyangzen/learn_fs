<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/kai.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/kai.hpp

## Purpose
This adapter configures Boost for KAI C++, another EDG-derived compiler.

## Important APIs, Types, And Control Flow
It includes `common_edg.hpp`, sets `BOOST_COMPILER`, and handles KAI-specific exception support with `__EXCEPTIONS`/`__KCC_EXCEPTIONS`. It rejects compilers older than 4.0 and optionally errors on versions newer than the known 4.0f table under `BOOST_ASSERT_CONFIG`.

## State And Persistence
It is preprocessor-only and has no runtime state.

## Dependencies And Integration Points
It depends on `__KCC_VERSION`, `__KCC`, exception macros, and common EDG config. It participates in Boost.Config compiler selection.

## Risks And Test Signals
Risks include narrow version coverage and reliance on common EDG defaults for most feature decisions. Test signals are KAI compile checks for exception mode, EDG inherited features, and version guard behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/kai.hpp -->
