# sources/user-network-fs/mergerfs/vendored/boost/core/detail/sp_win32_sleep.hpp

Purpose: Minimal Win32 declarations for `Sleep` and `SwitchToThread` without requiring `windows.h`, unless `BOOST_USE_WINDOWS_H` is requested.

Important APIs, types, and functions: Declares imported `Sleep(unsigned long)` and `SwitchToThread()` with the correct calling convention for supported Windows/Cygwin configurations.

Control flow: Preprocessor either includes `<windows.h>` or emits `extern "C" __declspec(dllimport)` declarations.

State and persistence behavior: No state.

Dependencies and integration points: Used by `sp_thread_sleep.hpp` and `sp_thread_yield.hpp`.

Risks: Calling convention and type-width macros are platform sensitive, especially Cygwin 64-bit and Clang x64. Declaration drift with Windows headers would break linkage.

Test signals: Compile with and without `BOOST_USE_WINDOWS_H` on MSVC, MinGW/Cygwin, and Clang-cl; link a small program calling sleep/yield primitives.
