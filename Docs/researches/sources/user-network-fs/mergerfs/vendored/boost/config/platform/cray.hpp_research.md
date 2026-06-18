# sources/user-network-fs/mergerfs/vendored/boost/config/platform/cray.hpp

Purpose: provides a minimal platform configuration for Cray systems.

Important APIs/macros: defines `BOOST_PLATFORM "Cray"` and `BOOST_HAS_UNISTD_H`, then includes POSIX feature detection.

Control flow/dependencies: static definition plus `boost/config/detail/posix_features.hpp`. The detailed capabilities are derived from Cray's POSIX macros in `<unistd.h>`.

State and persistence: compile-time macro state only.

Integration points: selected by `detail/select_platform_config.hpp` when `_CRAYC` is defined, and compiler selection separately chooses the Cray compiler config.

Risks and test signals: risk is under-specificity across Cray programming environments. Test POSIX feature derivation, pthread availability, timers, and standard headers under the target Cray compiler/runtime modules.
