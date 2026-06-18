<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/codegear.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/codegear.hpp

## Purpose
This adapter configures Boost for CodeGear/Embarcadero C++ compilers, covering both classic Borland-derived compilers and newer Clang-enhanced drivers.

## Important APIs, Types, And Control Flow
For Clang-based Embarcadero it includes `clang.hpp`, disables or corrects features known broken in the RTL/compiler, clears int128/float128 positives, marks missing cwchar/fenv/exception-header support, detects driver targets, and defines `BOOST_EMBTC_*` macros. For classic CodeGear it defines warning pragmas, defect macros for older versions, C++11 feature absences, TR1 support macros, stdint/MS int64/dirent support, ABI prefix/suffix paths, and compiler identity.

## State And Persistence
The file only modifies preprocessor and compiler-warning state. It may include `<cstring>` and `<errno.h>` to work around library issues; no runtime state is introduced.

## Dependencies And Integration Points
It is selected by Boost.Config and may delegate to Clang config. It integrates with Borland ABI headers and Windows platform selection through `BOOST_USE_WINDOWS_H`/`BOOST_DISABLE_WIN32`.

## Risks And Test Signals
Risks include the malformed-looking `#elif` target-detection branch, stale Embarcadero driver detection, and feature positives inherited from Clang that must be undone for the RTL. Test signals are classic and Clang Embarcadero compile tests, atomic/int128 checks, wide-char/fenv probes, and ABI wrapping tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/codegear.hpp -->
