# sources/user-network-fs/mergerfs/vendored/boost/predef/os/unix.h

Purpose: Detects generic Unix and SVR4 compilation environments for Boost.Predef. It defines `BOOST_OS_UNIX` and `BOOST_OS_SVR4`, plus availability/name macros, using only preprocessor feature macros.

Important APIs, types, and functions: Public API is macro-only: `BOOST_OS_UNIX`, `BOOST_OS_UNIX_AVAILABLE`, `BOOST_OS_UNIX_NAME`, `BOOST_OS_SVR4`, `BOOST_OS_SVR4_AVAILABLE`, and `BOOST_OS_SVR4_NAME`. It declares Predef tests with `BOOST_PREDEF_DECLARE_TEST`.

Control flow: Both macros start as `BOOST_VERSION_NUMBER_NOT_AVAILABLE`. `BOOST_OS_UNIX` becomes available when `unix`, `__unix`, `_XOPEN_SOURCE`, or `_POSIX_SOURCE` is defined. `BOOST_OS_SVR4` becomes available for System V markers such as `__sysv__`, `__SVR4`, `__svr4__`, or `_SYSTYPE_SVR4`.

State and persistence behavior: No runtime state or persistence exists; all behavior is compile-time macro state. Unlike more specific OS detectors, this file does not include `os_detected.h`, so it can coexist as an environment tag.

Dependencies and integration points: Depends on `boost/predef/version_number.h`, `boost/predef/make.h`, and `boost/predef/detail/test.h`. It is normally pulled by broader `boost/predef/os.h` or `boost/predef.h`.

Risks: Detection is intentionally broad; POSIX/X/Open feature macros can be defined on non-traditional Unix targets. Consumers needing a specific kernel or OS should prefer specific Predef OS macros.

Test signals: Boost.Predef self-test declarations exercise the resulting macro values when generated tests are enabled.
