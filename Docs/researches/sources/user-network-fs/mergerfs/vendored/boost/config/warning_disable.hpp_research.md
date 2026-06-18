# sources/user-network-fs/mergerfs/vendored/boost/config/warning_disable.hpp

Purpose: disables selected overly-pedantic compiler warnings for test cases or library source files.

Important APIs/macros: for MSVC 1400+ it disables warning C4996 for deprecated standard-library functions. For Intel (`__INTEL_COMPILER` or `__ICL`) it disables warning 1786 for similar deprecated-library diagnostics.

Control flow/dependencies: include guard and compiler-specific `#pragma warning(disable:...)` branches. The file intentionally includes no headers so warning suppression can happen before standard-library headers emit warnings.

State and persistence: compiler diagnostic state for the including translation unit.

Integration points: intended for tests or source files, explicitly not for normal Boost headers. It complements but does not depend on `boost/config.hpp`.

Risks and test signals: risk is hiding warnings that should be fixed or including it too late to matter. Test by compiling affected MSVC/Intel standard-library uses with and without the header and verifying no unrelated warnings are suppressed.
