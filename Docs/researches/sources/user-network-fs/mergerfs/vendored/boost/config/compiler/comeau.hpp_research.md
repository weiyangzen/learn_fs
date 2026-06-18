<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/comeau.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/comeau.hpp

## Purpose
This adapter configures Boost for Comeau C++, an EDG-based compiler.

## Important APIs, Types, And Control Flow
It includes `common_edg.hpp`, adds Comeau-specific fixes for older `__COMO_VERSION__` values, handles MSVC emulation quirks such as ADL and void returns, enables `BOOST_HAS_MS_INT64` under sufficiently new VC emulation, sets `BOOST_COMPILER`, and rejects unknown unsupported versions.

## State And Persistence
There is no runtime state; all effects are preprocessor macros.

## Dependencies And Integration Points
It depends on `__COMO_VERSION__`, optional `_MSC_VER`, and the common EDG config. It is selected by Boost.Config for Comeau and feeds all downstream Boost feature decisions.

## Risks And Test Signals
Risks include very narrow version support and reliance on EDG common assumptions. Test signals are compile-only Boost.Config checks under Comeau, with MSVC emulation variants for ADL, void return, and `__int64`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/comeau.hpp -->
