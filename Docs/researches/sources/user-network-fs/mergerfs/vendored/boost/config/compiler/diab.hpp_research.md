<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/diab.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/diab.hpp

## Purpose
This adapter configures Boost for the Diab C++ compiler.

## Important APIs, Types, And Control Flow
It includes `common_edg.hpp`, sets `BOOST_COMPILER` to `Diab C++ version` plus `__VERSION_NUMBER__`, and rejects versions earlier than 5.0.4.0. It otherwise relies on EDG common configuration for feature defects.

## State And Persistence
No runtime state is present. The header only defines preprocessor macros and errors on unsupported versions.

## Dependencies And Integration Points
It depends on EDG macros, `__VERSION_NUMBER__`, and `common_edg.hpp`. Boost.Config selects it for Diab and downstream code consumes the common EDG defect map.

## Risks And Test Signals
Risks are sparse Diab-specific overrides and stale version support. Test signals are compile-only Boost.Config checks under Diab, with emphasis on EDG features inherited from the common header and the version cutoff.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/diab.hpp -->
