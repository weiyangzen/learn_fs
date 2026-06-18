# sources/user-network-fs/mergerfs/vendored/boost/core/detail/sp_thread_pause.hpp

Purpose: Low-level spin-wait pause primitive for Boost smart pointer and concurrency internals.

Important APIs, types, and functions: `boost::core::sp_thread_pause()` emits architecture-specific pause/yield instructions through `BOOST_CORE_SP_PAUSE`.

Control flow: Preprocessor chooses x86 `_mm_pause`/`pause`, ARM `yield`, MSVC intrinsics, or an empty fallback. Runtime function is a single forced-inline instruction/macro invocation.

State and persistence behavior: No state.

Dependencies and integration points: Included by `yield_primitives.hpp` and fallback `sp_thread_yield.hpp`. Depends on Boost config and compiler architecture macros.

Risks: Incorrect architecture detection can emit unsupported assembly or lose spin-loop performance. Empty fallback is correct but may waste CPU under contention.

Test signals: Compile x86, ARM, MSVC, GCC/Clang paths; inspect generated assembly or run smoke tests in spin-wait code.
