<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/hp_acc.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/hp_acc.hpp

## Purpose
This adapter configures Boost for HP aC++.

## Important APIs, Types, And Control Flow
It defines `BOOST_COMPILER`, marks `BOOST_NO_TWO_PHASE_NAME_LOOKUP`, detects exception support from `__HPACC_NOEH`, enables `BOOST_HAS_LONG_LONG`, and for older versions defines numerous defects such as ADL absence, member template limitations, standard library issues, function ordering, SFINAE, template templates, and using-template limitations. It defines a broad set of C++11 absence macros and SD-6 checks for C++14/C++17 features, and rejects versions older than A.03.45.

## State And Persistence
The header only sets preprocessor macros. No runtime state is emitted.

## Dependencies And Integration Points
It depends on `__HP_aCC`, exception macros, and Boost.Config selection. Downstream Boost code uses these macros to avoid unsupported templates and standard-library facilities.

## Risks And Test Signals
Risks include old-version specific behavior, unconditional two-phase lookup disablement, and broad modern feature disables. Test signals are compile checks under HP aC++ versions for exceptions, templates, stdlib components, and C++11 feature gates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/hp_acc.hpp -->
