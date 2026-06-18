<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/cray.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/cray.hpp

## Purpose
This adapter configures Boost for Cray C++ Compiler Environment releases, with detailed version and language-mode handling.

## Important APIs, Types, And Control Flow
It computes `BOOST_CRAY_VERSION` from `_RELEASE_MAJOR`, `_RELEASE_MINOR`, and `_RELEASE_PATCHLEVEL`, including a special developer-build `x` patchlevel detector. It validates Cray version and EDG support, includes `common_edg.hpp`, defines a conservative baseline of missing C++11 features and Cray-specific threading/math macros, then conditionally undefines defects or adds positives for CCE 8.5, 8.6, 8.7, and later language modes. It also emulates `__GXX_EXPERIMENTAL_CXX0X__` in GCC mode and supplies atomic constants if absent.

## State And Persistence
The header is macro-only. It temporarily defines helper macros for version computation and undefines them at the end.

## Dependencies And Integration Points
It depends on Cray release macros, EDG markers, optional GCC-emulation macros, and `common_edg.hpp`. It feeds Boost libraries on Cray/HPC systems where compiler feature support changes sharply by release and language mode.

## Risks And Test Signals
Risks include incorrect developer-build patchlevel detection when `x` is user-defined, unsupported ISO dialects, and deliberately retained macros whose comments say tests are imperfect. Test signals are Boost.Config check-suite runs across CCE versions and C++03/11/14 modes, especially atomic, regex, value-initialization, and threading probes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/cray.hpp -->
