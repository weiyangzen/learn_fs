# sources/user-network-fs/mergerfs/vendored/boost/config/platform/win32.hpp

Purpose: configures Boost for native Win32 and related Windows targets.

Important APIs/macros: defines `BOOST_PLATFORM "Win32"`, may include `<_mingw.h>`, disables `swprintf` for GCC, defines default `BOOST_SYMBOL_EXPORT` and `BOOST_SYMBOL_IMPORT` as `__declspec(dllexport/dllimport)` plus `BOOST_HAS_DECLSPEC`, enables MinGW `BOOST_HAS_STDINT_H`, `BOOST_HAS_DIRENT_H`, `BOOST_HAS_UNISTD_H`, and `BOOST_HAS_GETTIMEOFDAY`, defaults to `BOOST_HAS_WINTHREADS` unless pthreads are already selected, handles WinCE/Windows Runtime with `BOOST_NO_ANSI_APIS`, and enables `BOOST_HAS_GETSYSTEMTIMEASFILETIME`, `BOOST_HAS_THREADEX`, `BOOST_HAS_FTIME`, and `BOOST_WINDOWS`.

Control flow/dependencies: Windows and MinGW conditionals; no POSIX feature include.

State and persistence: compile-time platform macros only.

Integration points: selected after Cygwin. Pairs with MSVC, MinGW GCC/Clang, and Dinkumware/MSVC STL configs. Symbol macros are used by Boost shared libraries.

Risks and test signals: risk is MinGW runtime version handling, WinCE/WinRT API restrictions, and symbol visibility defaults. Test native MSVC, clang-cl, MinGW, WinCE/WinRT, pthreads-for-Windows, auto-link, and dll import/export behavior.
