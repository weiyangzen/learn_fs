<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/gcc.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/gcc.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/gcc.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_GNUC`, `BOOST_COMP_GNUC_DETECTION`, `BOOST_COMP_GNUC_EMULATED`. Other relevant macros in this header include `BOOST_COMP_GNUC`, `BOOST_COMP_GNUC_DETECTION`, `BOOST_COMP_GNUC_EMULATED`, `BOOST_COMP_GNUC_AVAILABLE`, `BOOST_COMP_GNUC_NAME`. Display-name macros are `BOOST_COMP_GNUC_NAME` "Gnu GCC C/C++". Predef test registrations are `BOOST_COMP_GNUC,BOOST_COMP_GNUC_NAME`, `BOOST_COMP_GNUC_EMULATED,BOOST_COMP_GNUC_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__GNUC__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/compiler/clang.h`, `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/gcc.h -->
