# sources/user-network-fs/mergerfs/vendored/boost/config/detail/select_platform_config.hpp

Purpose: selects the platform-specific Boost.Config header by defining `BOOST_PLATFORM_CONFIG`.

Important APIs/macros: detects Linux/glibc, BSD variants, Solaris, IRIX, HP-UX, Cygwin, Win32, Haiku, BeOS, macOS, z/OS, AIX, AmigaOS, QNX, VxWorks, Symbian, Cray, VMS, CloudABI, WebAssembly, and generic Unix. Generic Unix defines `BOOST_HAS_UNISTD_H` and includes `detail/posix_features.hpp`.

Control flow/dependencies: ordered `#elif` chain. Cygwin intentionally precedes Win32 because it is not treated as native Win32. Cray is excluded from the Linux/glibc branch. The file uses quoted header names to avoid macro expansion in include names and contains a disabled dependency-scanner include list.

State and persistence: compile-time platform selection only.

Integration points: selected by `boost/config.hpp` unless disabled or overridden by `BOOST_PLATFORM_CONFIG` in user config.

Risks and test signals: risk is ambiguous platform macros, especially Cygwin/Win32, Cray/Linux, Apple/BSD, and z/OS/AIX IBM macros. Test by preprocessing target triples and verifying selected config plus POSIX feature macros.
