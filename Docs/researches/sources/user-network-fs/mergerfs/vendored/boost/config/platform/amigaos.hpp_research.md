# sources/user-network-fs/mergerfs/vendored/boost/config/platform/amigaos.hpp

Purpose: declares a conservative Boost platform profile for AmigaOS.

Important APIs/macros: defines `BOOST_PLATFORM "AmigaOS"`, disables threading with `BOOST_DISABLE_THREADS`, and marks wide-character support unavailable with `BOOST_NO_CWCHAR`, `BOOST_NO_STD_WSTRING`, and `BOOST_NO_INTRINSIC_WCHAR_T`.

Control flow/dependencies: no includes and no conditionals beyond normal preprocessing. It is a fixed capability profile.

State and persistence: compile-time macro state only.

Integration points: selected by `detail/select_platform_config.hpp` when `__amigaos__` is defined. `suffix.hpp` expands the wide-character implications and removes thread detail macros.

Risks and test signals: risk is underrepresenting newer AmigaOS ports with better C++ runtime support. Test with Boost.Config probes for wchar, std::wstring, and thread support if a maintained AmigaOS toolchain is available.
