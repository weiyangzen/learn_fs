# sources/user-network-fs/mergerfs/vendored/boost/config/platform/symbian.hpp

Purpose: configures Boost for Symbian OS.

Important APIs/macros: defines Symbian platform identity and applies a constrained embedded/mobile platform profile. The file adjusts standard-library and system-feature availability for Symbian, including threading, POSIX-like APIs, wide-character/string support, and C++ standard library gaps.

Control flow/dependencies: platform-specific preprocessor checks for Symbian SDK/compiler variants and optional includes. It is selected by `detail/select_platform_config.hpp` when `__SYMBIAN32__` is defined.

State and persistence: compile-time configuration only.

Integration points: interacts with compiler and stdlib configs for older mobile toolchains and lets `suffix.hpp` normalize disabled standard-library and thread features.

Risks and test signals: Symbian is legacy; the primary risk is stale SDK assumptions and untested combinations. Test signals are Boost.Config probes for threading, filesystem-like POSIX functions, wide-character support, exception/RTTI compatibility, and C++ library headers on the target SDK.
