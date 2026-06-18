# sources/user-network-fs/mergerfs/vendored/boost/core/detail/sp_thread_yield.hpp

Purpose: Provides a portable thread-yield primitive for spin/backoff code.

Important APIs, types, and functions: `boost::core::sp_thread_yield()` and Windows compatibility alias in `boost::detail`.

Control flow: Windows calls `SwitchToThread`. POSIX with scheduler support calls `sched_yield`. Fallback calls `sp_thread_pause`.

State and persistence behavior: No state.

Dependencies and integration points: Uses `sp_win32_sleep.hpp`, `<sched.h>`/AIX headers, or `sp_thread_pause.hpp`. Included by `yield_primitives.hpp` and sleep fallback.

Risks: Yield semantics vary by scheduler; fallback pause is not a true OS yield. AIX include path differs.

Test signals: Compile all platform branches; basic runtime call; integration with spin lock/backoff tests.
